require "json"

package = JSON.parse(File.read(File.join(__dir__, "../../../package.json")))

Pod::Spec.new do |s|
  s.name         = "HealthKitModule"
  s.version      = package["version"]
  s.summary      = "Local HealthKit Module"
  s.description  = "A local module for HealthKit integration"
  s.homepage     = "https://example.com"
  s.license      = "MIT"
  s.authors      = { "AVAFR" => "info@avafr.com" }
  s.platform     = :ios, "13.4"
  s.source       = { :git => ".", :tag => "#{s.version}" }

  s.source_files = "*.{h,m,mm}"
  s.dependency "React-Core"
end
