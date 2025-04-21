import av, torch, torchvision.transforms as T
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
from PIL import Image
import time, json, urllib.request

# ──────────────────────────────────────────────────────────────
# ❶ 모델 & 라벨 로드
weights = MobileNet_V3_Small_Weights.DEFAULT
model   = mobilenet_v3_small(weights=weights).eval().cuda()   # CUDA 사용 시
preproc = weights.transforms()

print("Model loaded:", model.__class__.__name__)

# 🏷️ ImageNet label dict (1‑1000)
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
classes = urllib.request.urlopen(LABELS_URL).read().decode().splitlines()

print("Label loaded:", len(classes), "classes")

# ──────────────────────────────────────────────────────────────
# ❷ SRT 수신 (listener)
src = "srt://0.0.0.0:6000?mode=listener&latency=20000"
container = av.open(
    src, options={"fflags": "nobuffer", "flags": "low_delay"}
)
stream = container.streams.video[0]

print("🟢 Listening on", src)
for packet in container.demux(stream):
    for frame in packet.decode():
        if frame.pts is None:        # (간혹 헤더 PTS 없을 때를 대비)
            continue

        pts_ms = float(frame.pts * frame.time_base) * 1000
        wall    = time.time() * 1000
        lag     = wall - pts_ms

        img = frame.to_ndarray(format="rgb24")
        pil = Image.fromarray(img)
        x   = preproc(pil).unsqueeze(0).cuda()

        with torch.no_grad():
            pred = model(x).softmax(dim=1)[0]
        idx  = int(pred.argmax())
        conf = float(pred[idx])

        print(
            f"PTS={pts_ms:,.0f} ms | now={wall:,.0f} ms | "
            f"lag≈{lag:5.0f} ms → {classes[idx]} ({conf:.2%})"
        )
