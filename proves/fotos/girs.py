# Turned copies of the given photos (as the app turns them) and their text recognition, for the "read again turned" path.
import sys, os, cv2, json
D = sys.argv[1]
for uid in sys.argv[2:]:
    im = cv2.imread(f'{D}/{uid}.jpg')
    for g, code in [(90, cv2.ROTATE_90_CLOCKWISE), (270, cv2.ROTATE_90_COUNTERCLOCKWISE), (180, cv2.ROTATE_180)]:
        cv2.imwrite(f'{D}/{uid}.g{g}.jpg', cv2.rotate(im, code))
