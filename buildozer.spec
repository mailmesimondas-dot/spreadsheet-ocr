[app]

# (string) Title of your application
title = Spreadsheet OCR

# (string) Package name
package.name = spreadsheet_ocr

# (string) Package domain (needed for unique android package name)
package.domain = org.antigravity

# (string) Source code directory
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas

# (string) Application versioning
version = 1.0.0

# (list) Application requirements
# Note: DO NOT add PyTorch or EasyOCR here. They will be run on the API server.
# Only Kivy and the requests library are needed on the phone client.
requirements = python3,kivy,requests,urllib3,idna,certifi,charset_normalizer

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions needed by the app
# Internet permission is required to talk to the API backend
# External storage permissions are required to download the resulting Excel file to the downloads folder
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk_path = 

# (str) Android SDK path to use
android.sdk_path = 

# (bool) Use gradle instead of ant
android.gradle_dependencies = 

# (list) List of Java .jar files to add to the libs so that pyjnius can access them
# (e.g. android.add_jars = foo.jar)
android.add_jars = 

# (list) Android features required by the application
# android.features = 

# (list) List of service to declare
# android.services = 

# (str) Bootstrap to use for android (sdl2, webview, etc.)
android.bootstrap = sdl2
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug and error)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
