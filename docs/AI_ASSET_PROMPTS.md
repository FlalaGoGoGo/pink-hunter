# Pink Hunter 手绘素材生成指令

## 通用正向提示词
`hand-drawn botanical illustration, pastel pink spring palette, soft watercolor + clean ink outline, high-end mobile product style, elegant negative space, transparent background, no text, no watermark, no logo`

## 通用反向提示词
`photorealistic, 3D render, noisy texture, cluttered background, typography, watermark, frame, low contrast, muddy colors`

## 参数建议
- `style strength: medium-high`
- `detail: high`
- `seed locked per asset`
- `export: transparent PNG`
- 图标额外约束: `flat vector-friendly shapes, bold silhouette, minimal tiny details`

## 资产逐项指令
1. `hero_cloud_blobs`
   - Size: `2048x1024`
   - Extra prompt: `soft irregular brush blobs, layered blush pink and peach tones, subtle paper grain, top banner composition`
2. `map_pin_cherry`
   - Size: `128x128`
   - Extra prompt: `single sakura blossom icon inside map pin silhouette, simple petals, high recognizability at 24px`
3. `map_pin_plum`
   - Size: `128x128`
   - Extra prompt: `single plum blossom icon inside map pin silhouette, rounder petals, distinct from cherry icon`
4. `map_pin_peach`
   - Size: `128x128`
   - Extra prompt: `single peach blossom icon inside map pin silhouette, elongated petals, distinct from cherry/plum`
5. `cluster_badge_shell`
   - Size: `256x256`
   - Extra prompt: `circular organic badge shell, hand-drawn ring, center left empty for number overlay`
6. `guide_compare_petals`
   - Size: `1600x1200`
   - Extra prompt: `triptych educational composition comparing cherry plum peach petal edges, scientific but friendly`
7. `guide_compare_pedicel`
   - Size: `1600x1200`
   - Extra prompt: `triptych comparing flower stalk length and cluster pattern`
8. `guide_compare_bark`
   - Size: `1600x1200`
   - Extra prompt: `triptych comparing bark lenticels and trunk texture`
9. `empty_state_spring_tree`
   - Size: `1200x1200`
   - Extra prompt: `single small spring tree with fallen petals, calm and hopeful mood`
10. `loading_doodle_loop_frames`
    - Size: `512x512` (12 frames)
    - Extra prompt: `simple rotating petal doodle sequence, consistent center and scale across frames`
11. `ownership_badges`
    - Size: `256x256`
    - Extra prompt: `three stamp-style hand-drawn badges: public private unknown, icon-only no text`
12. `share_sticker_pack`
    - Size: `1024x1024` (6 stickers)
    - Extra prompt: `set of 6 decorative spring stickers, petals, branches, tiny blossoms, no text`

## 替换流程
1. 用同名文件覆盖 `public/assets/ui/placeholders/` 中的占位素材。
2. 更新 `public/assets/ui/manifest.v1.json` 的 `format` 与 `generated_at`。
3. 提交后运行 `npm run build` 做前端校验。
