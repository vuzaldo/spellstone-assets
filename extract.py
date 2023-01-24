
import UnityPy
import cv2, numpy as np

def extract_images(file, save_dir = None, show = False):
	bundle = UnityPy.load(file)
	print(f'Reading {len(bundle.objects)} objects... ', end = '')
	textures, mono = {}, []
	for obj in bundle.objects:
		if obj.type.name == 'Texture2D':
			data = obj.read()
			img = data.image
			if not all(img.size): continue
			img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
			img = cv2.flip(img, 0)
			textures[obj.path_id] = img
		elif obj.type.name == 'MonoBehaviour':
			mono.append(obj)
	print(f'{len(textures)} Texture2D and {len(mono)} MonoBehaviour files found')
	for obj in mono:
		data = obj.read_typetree()
		if not data.get('textures'): continue
		texture_id = data['textures'][0]['m_PathID']
		if texture_id not in textures: continue
		texture = textures[texture_id]
		h, w = texture.shape[:2]
		for definitions in data['spriteDefinitions']:
			name = definitions['name']
			if not name: continue
			points = [tuple(uv.values()) for uv in definitions['uvs']]
			points = [(round(p[0] * w), round(p[1] * h)) for p in points]
			xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
			ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
			sprite = texture[ymin : ymin + (ymax - ymin), xmin : xmin + (xmax - xmin)]
			if not all(sprite.shape): continue
			if definitions['flipped']:
				sprite = cv2.rotate(sprite, cv2.ROTATE_90_COUNTERCLOCKWISE)
			else:
				sprite = cv2.flip(sprite, 0)
			print('\t', name)
			if save_dir:
				cv2.imwrite(f'{save_dir}/{name}.png', sprite)
			if show:
				cv2.imshow('Sprite', sprite)
				cv2.waitKey()
