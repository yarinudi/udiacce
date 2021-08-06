briefcase update android
briefcase build android
#briefcase run android -d @beePhone2
briefcase run android -d 216cc18c4f0d7ece
#adb logcat -s MainActivity:* stdio:* Python:*
adb -s 216cc18c4f0d7ece logcat -s MainActivity:* stdio:* Python:*
