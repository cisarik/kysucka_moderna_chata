#!/usr/bin/env fish
# Explicit local preview of the immutable seed; no automatic asset downloads.
set -l script_dir (path dirname (status filename))
set -l project_dir (path resolve "$script_dir/..")
set -l target "$project_dir/work/camera_a_preview.png"
if test -e "$target"
    echo "🛑 Náhľad už existuje: $target. Zachovaj ho a zvoľ nový výstup v úlohe."
    exit 2
end
set -l blender_bin (command -s blender)
if test -z "$blender_bin"; and test -x /Applications/Blender.app/Contents/MacOS/Blender
    set blender_bin /Applications/Blender.app/Contents/MacOS/Blender
end
if test -z "$blender_bin"
    echo "🛑 Blender nebol nájdený. Nič sa neinštalovalo."
    exit 2
end
echo "🎞️ Renderujem malý pracovný náhľad: $target"
"$blender_bin" --background --disable-autoexec "$project_dir/blender/kysucka_chata_seed.blend" --python-exit-code 2 --python "$project_dir/scripts/render_scene.py" -- --output "$target" --width 960 --samples 64
exit $status
