---
name: tomoviee-text-to-video
description: "使用万兴天幕（Tomoviee）AI大模型从文字描述生成视频。当用户需要：(1) 通过文字生成AI视频，(2) 创建短视频内容，(3) 将文案或创意转化为动态视频画面时使用此skill。即使用户只说'帮我生成一个视频'、'做一个XX的短视频'、'把这段描述变成视频'、'用天幕生成视频'等，也应该触发此 skill。支持多种画面比例和分辨率。"
tags:
  - ai-video
  - text-to-video
  - media-generation
  - tomoviee
version: 2.0.0
---

# 天幕文生视频（Tomoviee Text-to-Video）

通过天幕AI大模型，将文字描述转化为高质量视频。支持标准模式（720p）和高清模式（1080p），深度融合物理规律（动态光影、重力轨迹）与电影级运镜逻辑（推拉摇移/环绕调度）。

## 鉴权说明

天幕 API 使用 **access_key + secret** 的方式鉴权。完整鉴权流程如下：

### 用户需要提供的凭证

用户需要提供以下两个凭证（从 [天幕创作引擎控制台](https://www.tomoviee.cn/developers.html) 获取）：

- **access_key**：应用的 Access Key（也叫 App Key）
- **secret**：应用的 Secret Key

### 鉴权流程

**步骤1：获取 access_token**

使用 access_key 和 secret 调用 token 接口换取 access_token：

```
GET https://open-api.wondershare.cc/v1/open/capacity/get/token?access_key={access_key}&secret={secret}
```

返回示例：
```json
{
    "code": 0,
    "msg": "",
    "data": {
        "access_token": "Basic e2FjY2VzcyBrZXl9OntzZWNyZXR9"
    }
}
```

注意：返回的 `access_token` 值已包含 `Basic ` 前缀。

**步骤2：后续所有 API 请求携带两个认证 Header**

```
X-App-Key: {access_key}
Authorization: {access_token}
```

（`access_token` 已包含 `Basic ` 前缀，直接使用即可）

### 环境变量

运行脚本前需设置以下环境变量：

```bash
export TOMOVIEE_ACCESS_KEY="你的access_key"
export TOMOVIEE_SECRET="你的secret"
```

如果用户直接提供了 key 和 secret，可以直接在命令中设置环境变量后运行。

## Prompt 编写指南

天幕的 Prompt 公式：**主体(主体描述) + 运动 + 场景(场景描述) + (镜头语言 + 光影 + 氛围)**

- **主体**：视频中的主要表现对象（人、动物、植物、物体等）
- **主体描述**：外貌细节和肢体姿态（发型发色、服饰、五官、姿态等）
- **运动**：主体运动状态，需符合5-10秒视频内可展现的画面
- **场景**：主体所处的环境
- **镜头语言**（可选）：推拉摇移、环绕、低角度仰拍等
- **光影**（可选）：逆光、柔光、冷暖色调等
- **氛围**（可选）：温馨、科幻、史诗等

### Prompt 示例

| 级别 | Prompt |
|------|--------|
| 基础 | 一只柴犬在花田中奔跑 |
| 细节增强 | 一只橘黄色的柴犬在向日葵花田中欢快奔跑，阳光照射在它蓬松的毛发上，脖子上系着红色波点领巾，周围金黄色的向日葵随风摇曳，远处可见连绵的青山和蓝天白云 |
| 专业级 | 低角度仰拍，浅景深效果，逆光拍摄，一只橘黄色的柴犬在漫山遍野的向日葵中纵情奔跑 |

### Tips
- 尽量使用简单词语和句子结构
- 运动描述应符合物理规律
- 现阶段较难生成复杂的物理运动（如球类弹跳、高空抛物等）
- 描述与画面相差较大可能引起镜头切换

## 执行流程

使用 `scripts/tomoviee_text2video.py` 脚本来生成视频。该脚本自动处理完整流程：**获取token → 创建任务 → 轮询状态 → 下载视频**。

### 步骤 1：确认参数

向用户确认以下参数（仅 prompt 为必填）：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| prompt | 视频描述文字 | （必填） |
| duration | 视频时长，秒 | 5 |
| resolution | 分辨率：480p / 720p / 1080p | 720p |
| aspect_ratio | 画面比例：16:9 / 9:16 / 1:1 / 3:4 / 4:3 | 16:9 |
| camera_move_index | 镜头运动类型（整数，可选） | 无 |

帮助用户优化 prompt — 根据 Prompt 编写指南，在用户提供的简单描述基础上建议添加更多细节，但需用户确认最终 prompt。

### 步骤 2：运行脚本

```bash
export TOMOVIEE_ACCESS_KEY="用户的access_key"
export TOMOVIEE_SECRET="用户的secret"

python3 <skill-directory>/scripts/tomoviee_text2video.py \
  --prompt "视频描述" \
  --duration 5 \
  --resolution "720p" \
  --aspect_ratio "16:9" \
  --output ~/Desktop/
```

其中 `<skill-directory>` 是本 skill 的安装路径。

可选参数：
- `--camera_move_index N` — 镜头运动类型
- `--callback "http://..."` — 回调地址
- `--params "..."` — 透传参数
- `--poll_interval 10` — 轮询间隔秒数（默认10）
- `--max_wait 600` — 最大等待秒数（默认600）
- `--download` — 加上此参数会下载视频到本地（默认仅输出链接）
- `--output ~/Desktop/` — 下载目录（仅在 --download 时生效）

### 步骤 3：展示结果

脚本执行成功后，会输出生成的视频链接（URL）。将视频链接展示给用户，用户可以直接在浏览器中打开或下载。

## 预期输出

- **类型**：视频链接（URL）
- **格式**：可直接访问的 .mp4 视频链接
- **操作**：展示链接给用户，用户可在浏览器打开或下载

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 环境变量未设置 | 提示用户设置 `TOMOVIEE_ACCESS_KEY` 和 `TOMOVIEE_SECRET` |
| Token 获取失败 | 检查 access_key 和 secret 是否正确 |
| 余额不足 (insufficient balance) | 提示用户前往 https://app.tomoviee.cn/pricing 充值积分 |
| API 返回非0错误码 | 显示错误信息，建议检查凭证或修改 prompt |
| 任务超时 (status=6) | 建议简化 prompt 或稍后重试 |
| 任务失败 (status=4) | 显示失败原因，建议调整参数后重试 |

## API 参考

### 文生视频 - 创建任务

- **URL**: `POST https://open-api.wondershare.cc/v1/open/capacity/application/tm_text2video_b`
- **Headers**: `Content-Type: application/json`, `X-App-Key: {access_key}`, `Authorization: {access_token}`
- **Body**: `{"prompt": "...", "duration": 5, "resolution": "720p", "aspect_ratio": "16:9"}`
- **返回**: `{"code": 0, "data": {"task_id": "..."}}`

### 查询任务结果

- **URL**: `POST https://open-api.wondershare.cc/v1/open/pub/task`
- **Headers**: 同上
- **Body**: `{"task_id": "..."}`
- **任务状态**: 1-排队中, 2-处理中, 3-成功, 4-失败, 5-已取消, 6-已超时
- **成功返回**: result 字段包含 JSON 字符串，内含 `video_path` 数组（视频下载链接）
