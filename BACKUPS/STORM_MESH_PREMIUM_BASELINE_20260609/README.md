# Storm Mesh Premium — baseline backup (2026-06-09)

Полный путь:
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/backups/STORM_MESH_PREMIUM_BASELINE_20260609/`

- MANIFEST.txt — 79 файлов (§4 + §4.1 + Colors.swift)
- Screens/ — копии до Storm Mesh
- Shared/Styles/Colors.swift

Восстановить файл:
`cp -p backups/STORM_MESH_PREMIUM_BASELINE_20260609/Screens/<File>.swift Screens/<File>.swift`

Восстановить все экраны:
`rsync -a backups/STORM_MESH_PREMIUM_BASELINE_20260609/Screens/ Screens/`
