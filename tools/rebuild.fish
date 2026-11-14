#!/usr/bin/env fish
# Explicit local generator. Run only under an authorized Worker/user task.
set -l script_dir (path dirname (status filename))
set -l project_dir (path resolve "$script_dir/..")
set -l target "$project_dir/work/rebuild.blend"
if test -e "$target"
    echo "🛑 Výstup už existuje: $target. Zachovaj ho a zvoľ nový výstup v úlohe."
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
echo "🧱 Tvorím pracovnú kópiu: $target"
"$blender_bin" --background --factory-startup --python-exit-code 2 --python "$project_dir/scripts/build_scene.py" -- --output "$target"
exit $status
