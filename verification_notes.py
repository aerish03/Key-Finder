
# Offline regression checks based on current SongBPM pages verified during build:
# The web lookup showed:
#   The Local Train - Aaoge Tum Kabhi: 98 BPM, C
#   The Local Train - Choo Lo: 146 BPM, E
# These are not hard-coded into the app; they are only sanity references.
EXPECTED = {
    ("The Local Train", "Aaoge Tum Kabhi"): (98, "C"),
    ("The Local Train", "Choo Lo"): (146, "E"),
}
