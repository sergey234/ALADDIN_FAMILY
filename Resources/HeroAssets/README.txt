Hero onboarding art — how not to get lost
==========================================

Brand wordmark «ALADDIN AI» (V2, не hero):
  Resources/BrandAssets/ALADDIN_AI_V2_Logo/
  Копия на Mac: ~/Downloads/ALADDIN_AI_V2_Logo/

1) Name the code expects (do not rename)
   - Asset catalog image set: OnboardingHero_00 … OnboardingHero_07, MainHero_ambient
   - See Shared/Components/HeroAmbientPresentation.swift (HeroPresentation)

2) Two folders, two roles
   - Resources/HeroAssets/OnboardingHero_00.png
     = full-resolution master (1536×1024 or whatever design exports). For version control and re-export.
     = NOT added to “Copy Bundle Resources”; app does not load UIImage from here.

   - Assets.xcassets/OnboardingHero_00.imageset/OnboardingHero_00.png
     = what the app actually ships (393×852 portrait from the master).
     = UIImage(named: "OnboardingHero_00") reads THIS file.
     = MUST live directly under Assets.xcassets (not inside nested Images.xcassets — actool does not merge nested *.xcassets; names there resolve to nil at runtime).

3) When art changes
   - Drop new master into Resources/HeroAssets/OnboardingHero_00.png (replace file, keep name).
   - Regenerate the catalog PNG (same 393×852 cover crop from center) into the .imageset, or export @1x/@2x/@3x per docs/ALADDIN_Hero_Asset_Pipeline.md and update Contents.json.
   - Optional Figma zone reference: OnboardingHero_00_figma_zone_361x460.png (see docs/ONBOARDING_OB_00_EXPORT_LOG.md).

4) Quick check after build
   - Console: "HeroAmbientLayerView: Using raster image for OnboardingHero_00"
   - If you see "No asset found" — the .imageset is missing PNG or Contents.json filenames are wrong.
