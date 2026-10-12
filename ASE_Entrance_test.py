import json
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen


def get_json(url):
    try:
        with urlopen(url, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise


with open("requirements.txt", encoding="utf-8") as file:
    dependencies = [
        line.split("#", 1)[0].strip()
        for line in file
        if line.split("#", 1)[0].strip() and "==" in line
    ]

packages_not_found = 0
versions_not_found = 0
oldest = None

for dependency in dependencies:
    name, version = [part.strip() for part in dependency.split("==", 1)]
    package_url = f"https://pypi.org/pypi/{quote(name, safe='')}/json"

    if get_json(package_url) is None:
        packages_not_found += 1
        continue

    version_url = (
        f"https://pypi.org/pypi/{quote(name, safe='')}/"
        f"{quote(version, safe='')}/json"
    )
    release = get_json(version_url)

    if release is None:
        versions_not_found += 1
        continue

    upload_times = [
        file.get("upload_time_iso_8601") or file.get("upload_time")
        for file in release.get("urls", [])
    ]
    upload_times = [time for time in upload_times if time]

    if upload_times:
        release_time = min(upload_times)
        if oldest is None or release_time < oldest[0]:
            oldest = (release_time, f"{name}=={version}")

print(f"Dependecies checked: {len(dependencies)}")
print(f"Packages not on PyPI: {packages_not_found}")
print(f"Versions not on PyPI: {versions_not_found}")

if oldest:
    print(f"Oldest pinned release: {oldest[1]}")
else:
    print("Oldest pinned release: None")