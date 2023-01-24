
import os, requests
from extract import extract_images

# Assets URL and version may change
url = 'https://d3splaxnu2bep2.cloudfront.net/spellstone/asset_bundles_live/2020_3_33f1/'
version = '_unity2020_3_33_webgl.unity3d'

output_dir = 'assets/'
show_images = False # show each extracted image
image_format = 'png'
# image_format = 'jpg' # loses alpha/transparency
# Save the content of each .unity3d file in a separate folder instead of grouping types
split_folder = True

def asset_counter(asset):
	i = asset.index('{') if '{' in asset else len(asset)
	name, z = asset[:i], asset[i + 1 : -1]
	name = name[:-1] if name[-1] == '_' else name
	z = int(z) if z else 0
	k = 1
	# Find the next asset number we don't have extracted (only with split_folder mode)
	if split_folder:
		dirs = sorted(d for d in os.listdir(output_dir) if os.path.isdir(output_dir + d))
		last = [d for d in dirs if name in d]
		last = last[-1] if last else ''
		k = last[last.rindex('_') + 1:] if '_' in last else ''
		k = int(k) + 1 if k.isdigit() else 1
	return name, z, k

# We are not interested in these (also some are incomplete or only contained in core assets)
assets = '''arena_boxes_{3} core_assets_{3} event{1} event_{3} frog_crystal_{2} guildwars_{3} item_{3}
localizationpack_{3} mappack_{3} pvp_bundle_{3} raid_{3} santaBundle_{3} storepack_{3} skills_{3} bgeIcons_{3}
challenge_banners_{3} cardpack_standardset_2020 dungeon_{3}'''
# Not updated often
assets = 'cardpack_{3} cardpack_expansion_{3} cardpack_aprilfools_{3} runepack_{3} mapbanners_{3}'
# Updated every new BGE (portraitpack for the LBN)
assets = 'cardpack_event_{3} portraitpack_{3}'

# Sometimes the same asset is reused to add new content
force_rewrite = { 'portraitpack': 7 }

assets = assets.split()
print(f'Trying to download {len(assets)} asset types:', ' '.join(assets))

for asset in assets:
	print()
	name, z, k = asset_counter(asset)
	f = force_rewrite.get(name, k)
	if f < k:
		k = f
		print(f'[Rewriting assets from {name}_{str(k).zfill(z)}+]')
	while True:
		num = str(k).zfill(z) if z else ''
		sep = '_' if num else ''
		file = name + sep + num + version
		link = url + file
		print(f'{assets.index(asset) + 1}/{len(assets)}', name, f'#{num}', '\nURL:', link)
		res = requests.get(link)
		if res.status_code == 200:
			print('New asset!')
			# with open(output_dir + file, 'wb') as f: f.write(res.content) # to save the .unity3d file
			folder = output_dir + name + (sep + num if split_folder else '')
			os.makedirs(folder, exist_ok = True)
			extract_images(res.content, save_dir = folder, show = show_images, img_format = image_format)
		else:
			print(f'Not found ({res.status_code})')
			break
		if not z: # no asset numbering (_0 ~ _000 extension)
			break
		k += 1
		# break
