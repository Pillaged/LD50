package loader

import (
	"bytes"
	"embed"
	"image"

	_ "image/png"

	"github.com/Pillaged/LD50/server/rpc"
	"golang.org/x/image/draw"
)

//go:embed collision_map_1.png
var words embed.FS

type Loader struct {
	collision_maps map[string]*rpc.GetCollisionMapResp
}

func New() (*Loader, error) {
	content, err := words.ReadFile("collision_map_1.png")
	if err != nil {
		return nil, err
	}
	imageData, imageType, err := image.Decode(bytes.NewReader(content))
	if err != nil {
		panic(err)
	}
	print(imageType)

	bounds := imageData.Bounds()
	width, height := bounds.Max.X, bounds.Max.Y

	pixels := image_2_array_pix(imageData)
	collision := pix_to_collision(pixels)
	collision_map := &rpc.GetCollisionMapResp{
		Width:  int64(width),
		Height: int64(height),
		Data:   collision,
	}

	words := &Loader{
		collision_maps: map[string]*rpc.GetCollisionMapResp{},
	}
	words.collision_maps["test_0"] = collision_map
	return words, nil
}

func image_2_array_pix(src image.Image) [][][3]uint8 {
	bounds := src.Bounds()
	width, height := bounds.Max.X, bounds.Max.Y
	iaa := make([][][3]uint8, height)
	src_rgba := image.NewRGBA(src.Bounds())
	draw.Copy(src_rgba, image.Point{}, src, src.Bounds(), draw.Src, nil)

	for y := 0; y < height; y++ {
		row := make([][3]uint8, width)
		for x := 0; x < width; x++ {
			idx_s := (y*width + x) * 4
			pix := src_rgba.Pix[idx_s : idx_s+4]
			row[x] = [3]uint8{(pix[0]), (pix[1]), (pix[2])}
		}
		iaa[y] = row
	}

	return iaa
}

func pix_to_collision(src [][][3]uint8) []rpc.GetCollisionMapResp_Collision {
	w := len(src[0])

	iaa := make([]rpc.GetCollisionMapResp_Collision, len(src[0])*len(src[1]))
	for y := 0; y < len(src); y++ {
		for x := 0; x < len(src[0]); x++ {
			switch src[y][x] {
			case [3]uint8{255, 0, 0}:
				iaa[x+y*w] = rpc.GetCollisionMapResp_WALL
			case [3]uint8{0, 0, 0}:
				iaa[x+y*w] = rpc.GetCollisionMapResp_EMPTY
			default:
				iaa[x+y*w] = rpc.GetCollisionMapResp_EMPTY
			}
		}
	}
	return iaa
}
