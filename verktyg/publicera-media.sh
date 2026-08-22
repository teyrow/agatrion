#!/bin/bash
# Synka ljud och video till objektlagringen hos GleSYS.
#
# Mediafilerna ligger inte i git — de är stora och ändras aldrig. De bor här på
# disk under media/ljud och media/video, och den här skriptet lägger upp dem i
# en S3-bucket som sajten sedan länkar till.
#
#   ./verktyg/publicera-media.sh --test    visar vad som skulle hända
#   ./verktyg/publicera-media.sh           laddar upp det som saknas eller ändrats
#   ./verktyg/publicera-media.sh --stada   tar dessutom bort filer i bucketen
#                                          som inte längre finns lokalt
#
# Kräver s3cmd (brew install s3cmd) och en konfigurerad ~/.s3cfg, se README.

set -euo pipefail

BUCKET="${AGATRION_BUCKET:-agatrion-media}"
DC="${AGATRION_DC:-dc-fbg1}"
ROT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAPPAR=(ljud video)

TORR=""
STADA=""
for arg in "$@"; do
  case "$arg" in
    --test)  TORR="--dry-run" ;;
    --stada) STADA="--delete-removed" ;;
    *) echo "Okänt argument: $arg" >&2; exit 2 ;;
  esac
done

command -v s3cmd >/dev/null || { echo "s3cmd saknas. Installera med: brew install s3cmd" >&2; exit 1; }
[ -f "$HOME/.s3cfg" ] || { echo "~/.s3cfg saknas. Kör 's3cmd --configure', se README." >&2; exit 1; }

# Filerna byter aldrig innehåll, så de får cachas för alltid. Byter du ut en
# inspelning måste den också få ett nytt filnamn.
CACHE="Cache-Control:public, max-age=31536000, immutable"

for mapp in "${MAPPAR[@]}"; do
  kalla="$ROT/media/$mapp"
  [ -d "$kalla" ] || { echo "hoppar över $mapp (finns inte)"; continue; }
  echo "== $mapp -> s3://$BUCKET/$mapp/"
  s3cmd sync $TORR $STADA \
    --acl-public \
    --no-preserve \
    --guess-mime-type \
    --add-header="$CACHE" \
    --exclude '.DS_Store' \
    "$kalla/" "s3://$BUCKET/$mapp/"
done

if [ -z "$TORR" ]; then
  echo
  echo "Klart. Kontrollera en fil:"
  echo "  curl -sI https://$BUCKET.objects.$DC.glesys.net/ljud/tranas-2026/01-franz-schubert-schubert.mp3 | head -3"
fi
