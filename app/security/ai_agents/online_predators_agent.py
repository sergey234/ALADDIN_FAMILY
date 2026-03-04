# -*- coding: utf-8 -*-
"""
OnlinePredatorsAgent (CNN + RNN)
--------------------------------

Модуль S1-15/S1-16 объединяет:
1. CNN-блок — анализ изображений (аватары, вложения, скриншоты переписок).
2. RNN-блок — анализ текстов/сообщений от потенциальных хищников.

Дальнейшие этапы расширят модель Transformer-слоем, но базовый функционал уже
позволяет тренировать и запускать оба канала отдельно и комбинировать результаты.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import torch
from PIL import Image
from torch import nn
from torch.nn.utils.rnn import pad_packed_sequence, pad_sequence, pack_padded_sequence
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from security.base import SecurityBase


@dataclass
class CNNConfig:
    """Конфигурация CNN-части агента."""

    image_size: Tuple[int, int] = (224, 224)
    num_classes: int = 2
    dropout: float = 0.3
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    device: Optional[str] = None  # cuda / mps / cpu


class OnlinePredatorsImageDataset(Dataset):
    """Минимальный датасет для загрузки изображений и меток."""

    def __init__(
        self,
        samples: Sequence[Tuple[Path, int]],
        image_size: Tuple[int, int],
    ) -> None:
        self.samples = samples
        self.transform = transforms.Compose(
            [
                transforms.Resize(image_size),
                transforms.CenterCrop(image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        image_path, label = self.samples[idx]
        image = Image.open(image_path).convert("RGB")
        return self.transform(image), torch.tensor(label, dtype=torch.long)


class OnlinePredatorsCNN(nn.Module):
    """Простая CNN-сеть: Conv → BN → ReLU → Pool блоки + классификатор."""

    def __init__(self, num_classes: int, dropout: float = 0.3) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((7, 7)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 7 * 7, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        x = self.features(x)
        return self.classifier(x)


@dataclass
class RNNConfig:
    """Конфигурация текстового блока."""

    embedding_dim: int = 256
    hidden_dim: int = 256
    num_layers: int = 2
    dropout: float = 0.3
    num_classes: int = 2
    max_vocab_size: int = 25000


class Vocabulary:
    """Простейший менеджер словаря для RNN части."""

    PAD = "<pad>"
    UNK = "<unk>"

    def __init__(self, max_size: int = 25000) -> None:
        self.max_size = max_size
        self.token_to_idx = {self.PAD: 0, self.UNK: 1}
        self.idx_to_token = [self.PAD, self.UNK]
        self.token_pattern = re.compile(r"[\\w']+")

    def __len__(self) -> int:
        return len(self.idx_to_token)

    @property
    def pad_idx(self) -> int:
        return self.token_to_idx[self.PAD]

    def add_sentence(self, sentence: str) -> None:
        for token in self.token_pattern.findall(sentence.lower()):
            if token not in self.token_to_idx:
                if len(self.idx_to_token) >= self.max_size:
                    break
                self.token_to_idx[token] = len(self.idx_to_token)
                self.idx_to_token.append(token)

    def encode(self, sentence: str) -> List[int]:
        return [self.token_to_idx.get(token, 1) for token in self.token_pattern.findall(sentence.lower())]


class OnlinePredatorsTextEncoder(nn.Module):
    """BiLSTM-классификатор подозрительных сообщений."""

    def __init__(self, config: RNNConfig, vocab_size: int) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, config.embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=config.embedding_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            dropout=config.dropout,
            bidirectional=True,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.Linear(config.hidden_dim * 2, config.hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, config.num_classes),
        )

    def forward(self, inputs: torch.Tensor, lengths: List[int]) -> torch.Tensor:
        embedded = self.embedding(inputs)
        packed = pack_padded_sequence(embedded, lengths=lengths, batch_first=True, enforce_sorted=False)
        packed_outputs, _ = self.lstm(packed)
        outputs, _ = pad_packed_sequence(packed_outputs, batch_first=True)
        last_indices = torch.tensor([l - 1 for l in lengths], device=inputs.device)
        last_hidden = outputs[torch.arange(outputs.size(0)), last_indices]
        return self.classifier(last_hidden)


class OnlinePredatorsAgent(SecurityBase):
    """
    Гибридный агент: CNN по изображениям + RNN по текстам.
    Единый интерфейс позволяет использовать оба сигнала по отдельности и комбинировать результаты.
    """

    def __init__(
        self,
        cnn_config: Optional[CNNConfig] = None,
        rnn_config: Optional[RNNConfig] = None,
        cnn_weights_path: Optional[Path] = None,
        rnn_weights_path: Optional[Path] = None,
        vocabulary: Optional[Vocabulary] = None,
    ) -> None:
        super().__init__("OnlinePredatorsAgent")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cnn_config = cnn_config or CNNConfig()
        self.rnn_config = rnn_config or RNNConfig()
        self.device = torch.device(self.cnn_config.device or ("cuda" if torch.cuda.is_available() else "cpu"))

        self.cnn_model = OnlinePredatorsCNN(
            num_classes=self.cnn_config.num_classes,
            dropout=self.cnn_config.dropout,
        ).to(self.device)
        if cnn_weights_path:
            self.load_cnn_weights(cnn_weights_path)

        self.vocab = vocabulary or Vocabulary(max_size=self.rnn_config.max_vocab_size)
        self.text_encoder = OnlinePredatorsTextEncoder(self.rnn_config, vocab_size=len(self.vocab)).to(self.device)
        if rnn_weights_path:
            self.load_rnn_weights(rnn_weights_path)

    # ------------------------------------------------------------------ #
    #   ПРЕДОБРАБОТКА / ИНФЕРЕНС
    # ------------------------------------------------------------------ #
    @property
    def transform(self):
        return transforms.Compose(
            [
                transforms.Resize(self.cnn_config.image_size),
                transforms.CenterCrop(self.cnn_config.image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def _prepare_tensor(self, image: Image.Image) -> torch.Tensor:
        tensor = self.transform(image).unsqueeze(0)
        return tensor.to(self.device)

    def predict_image(self, image_path: Path) -> dict:
        image = Image.open(image_path).convert("RGB")
        tensor = self._prepare_tensor(image)
        self.cnn_model.eval()
        with torch.no_grad():
            logits = self.cnn_model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
            confidence, label = torch.max(probs, dim=0)

        result = {
            "image": str(image_path),
            "label": label.item(),
            "confidence": round(confidence.item(), 4),
            "probabilities": probs.cpu().tolist(),
        }
        self.logger.debug("CNN prediction", extra=result)
        return result

    def predict_batch(self, image_paths: Iterable[Path]) -> List[dict]:
        return [self.predict_image(path) for path in image_paths]

    # ------------------------------------------------------------------ #
    #   ОБУЧЕНИЕ
    # ------------------------------------------------------------------ #
    def create_dataloader(
        self,
        samples: Sequence[Tuple[Path, int]],
        batch_size: int = 8,
        shuffle: bool = True,
    ) -> DataLoader:
        dataset = OnlinePredatorsImageDataset(samples, self.cnn_config.image_size)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=2)

    def train_epoch(
        self,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
    ) -> Tuple[float, float]:
        self.cnn_model.train()
        running_loss = 0.0
        running_correct = 0
        total = 0

        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            optimizer.zero_grad()
            outputs = self.cnn_model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            running_correct += (preds == labels).sum().item()
            total += labels.size(0)

        avg_loss = running_loss / max(total, 1)
        accuracy = running_correct / max(total, 1)
        self.logger.info("CNN epoch stats", extra={"loss": avg_loss, "accuracy": accuracy})
        return avg_loss, accuracy

    def finetune(
        self,
        train_loader: DataLoader,
        epochs: int = 3,
    ) -> List[Tuple[float, float]]:
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(
            self.cnn_model.parameters(),
            lr=self.cnn_config.learning_rate,
            weight_decay=self.cnn_config.weight_decay,
        )

        history: List[Tuple[float, float]] = []
        for epoch in range(epochs):
            loss, acc = self.train_epoch(train_loader, optimizer, criterion)
            history.append((loss, acc))
            self.logger.info(
                "Epoch finished",
                extra={"epoch": epoch + 1, "loss": loss, "accuracy": acc},
            )
        return history

    # ------------------------------------------------------------------ #
    #   УПРАВЛЕНИЕ ВЕСАМИ
    # ------------------------------------------------------------------ #
    def load_cnn_weights(self, path: Path) -> None:
        state_dict = torch.load(path, map_location=self.device)
        self.cnn_model.load_state_dict(state_dict)
        self.logger.info("CNN weights loaded", extra={"path": str(path)})

    def save_cnn_weights(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.cnn_model.state_dict(), path)
        self.logger.info("CNN weights saved", extra={"path": str(path)})

    # ------------------------------------------------------------------ #
    #   ТЕКСТОВАЯ ЧАСТЬ
    # ------------------------------------------------------------------ #
    def build_vocab(self, texts: Sequence[str]) -> None:
        for text in texts:
            self.vocab.add_sentence(text)
        # пересоздаём текстовый энкодер с новым размером словаря
        self.text_encoder = OnlinePredatorsTextEncoder(self.rnn_config, vocab_size=len(self.vocab)).to(self.device)

    def _encode_texts(self, texts: Sequence[str]) -> Tuple[torch.Tensor, List[int]]:
        sequences = [torch.tensor(self.vocab.encode(text), dtype=torch.long) for text in texts]
        lengths = [len(seq) if len(seq) > 0 else 1 for seq in sequences]
        padded = pad_sequence(
            [seq if len(seq) > 0 else torch.tensor([self.vocab.pad_idx]) for seq in sequences],
            batch_first=True,
            padding_value=self.vocab.pad_idx,
        )
        return padded.to(self.device), lengths

    def predict_text(self, text: str) -> dict:
        return self.predict_text_batch([text])[0]

    def predict_text_batch(self, texts: Sequence[str]) -> List[dict]:
        if not texts:
            return []
        inputs, lengths = self._encode_texts(texts)
        self.text_encoder.eval()
        with torch.no_grad():
            logits = self.text_encoder(inputs, lengths)
            probs = torch.softmax(logits, dim=1)
            conf, labels = torch.max(probs, dim=1)

        return [
            {
                "text_preview": text[:200],
                "label": labels[i].item(),
                "confidence": round(conf[i].item(), 4),
                "probabilities": probs[i].cpu().tolist(),
            }
            for i, text in enumerate(texts)
        ]

    def load_rnn_weights(self, path: Path) -> None:
        state_dict = torch.load(path, map_location=self.device)
        self.text_encoder.load_state_dict(state_dict)
        self.logger.info("RNN weights loaded", extra={"path": str(path)})

    def save_rnn_weights(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.text_encoder.state_dict(), path)
        self.logger.info("RNN weights saved", extra={"path": str(path)})


__all__ = [
    "OnlinePredatorsAgent",
    "CNNConfig",
    "OnlinePredatorsCNN",
    "RNNConfig",
    "OnlinePredatorsTextEncoder",
    "Vocabulary",
]

