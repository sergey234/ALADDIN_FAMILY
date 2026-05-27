# Uncomment the next line to define a global platform for your project
platform :ios, '15.0'

target 'ALADDIN' do
  # Comment the next line if you don't want to use dynamic frameworks
  use_frameworks!

  # Pods for ALADDIN Family Security App
  # External dependencies only (system frameworks are built-in)
  
  # Networking and API
  pod 'Alamofire', '~> 5.8'
  pod 'Moya', '~> 15.0'
  
  # Data and Storage
  pod 'KeychainAccess', '~> 4.2'
  
  # E1.4 E2EE (optional — requires `pod install` + ALADDIN.xcworkspace)
  # ENV['LIBSIGNAL_FFI_PREBUILD_CHECKSUM'] = 'e3b89de2afc950c9e317f2fff426ae8edc77a397520d2e0afbb717d738213fd5'
  # pod 'LibSignalClient', :git => 'https://github.com/signalapp/libsignal.git', :tag => 'v0.94.1'

  # UI and Animation
  pod 'Lottie', '~> 4.3'
  # HERO-3-08: дублирует SPM `rive-ios` в xcodeproj (если собираете через .xcworkspace)
  pod 'RiveRuntime', '~> 6.0'
  pod 'SDWebImageSwiftUI', '~> 2.2'
  
  # Testing
  pod 'Quick', '~> 7.0'
  pod 'Nimble', '~> 12.0'

  target 'ALADDINTests' do
    inherit! :search_paths
    # Pods for testing
  end

  target 'ALADDINUITests' do
    # Pods for testing
  end

end
