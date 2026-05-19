#!/usr/bin/env python3
r"""
MATLAB P-Code 转换测试脚本
===========================

从当前目录随机选取一个 .p 文件，或指定某个 .p 文件，通过 base64 编码后
发送到 pcode.948421.xyz 的 `/api/showcase/convert` 接口，获取转换结果、
报价信息和脱敏预览。依赖 Python 标准库，无需额外安装。

用法
----
    python send_pcode.py             随机选取当前目录下的 .p 文件发送
    python send_pcode.py test.p      指定 test.p 发送
    python send_pcode.py <file.p>    指定任意 .p 文件发送

当前目录无 .p 文件时自动回退到内置的 v02.p（硬编码在脚本中）。

免责声明
--------
本脚本仅供学习和测试用途。使用者对发送的文件内容及 API 调用行为负全部责任。
请勿用于非法目的。作者对误用、滥用或由此产生的任何直接/间接损害概不负责。
"""

import base64
import json
import os
import random
import sys
import textwrap
import time
import urllib.error
import urllib.request

import base64
import json
import os
import random
import sys
import textwrap
import time
import urllib.error
import urllib.request

API_URL = "https://pcode.948421.xyz/api/showcase/convert"

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://pcode.948421.xyz",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://pcode.948421.xyz/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
}

# 内置默认 v02.p（2235 bytes），当目录下没有 .p 文件时回退使用
# 内置默认 v02.p（2235 bytes），当目录下没有 .p 文件时回退使用
_FALLBACK_V02_P_B64 = (
    "djAyLjAydjAyLjAyAAAAgHmljf0AAAAAAAAImwAACJtQSwMEFAAAAAgAAAAhADs6JjHNAA"
    "AAZgEAABMAAABbQ29udGVudF9UeXBlc10ueG1spZAxbsMwDEV3n0Lg7tDtUBSF5QwFMqYd"
    "0gMwMusIkShBIor49pXTtejShQDB/x8eOO5vMZgvLtUnsfCwG8CwuDR7WSx8nA79M5iqJD"
    "OFJGxh5QpmP3Xjac1cTWtLtXBRzS+I1V04Ut2lzNIun6lE0raWBTO5Ky2Mj8PwhC6Jsmiv"
    "GwOmzpjxrTkUP7N5/blteAuUc/COtMlhcsraVy1MEcw7FT1SbBnMTZfx7IXKCvgHTfmmmA"
    "N5+aW/jS32H0LMTfXsg9e7yIj3J03dN1BLAwQUAAAAAAAAACEAr5Yb1voFAAD6BQAADAAA"
    "AHBjb2RlL2JpbmFyeRQ8PDzfhFfDG8E2R2ZjWzY/iiwBRBe7LL9tdEjIRiKj5+SdwaOxce"
    "ZyeiHtoB9Kx4WH7CBr50pdHXh7srRIt3ZQyd0q6ckymxtTnA4XnaYy1qmSdeZAv3FRYexA"
    "KVldE+6sflnHoo9ABBBSrar70ShPFw6jrUdVKObXpauu2F74ZfG32gIUS/juwYY6FowhsW"
    "wQILzkTlL3jdKGdSCGXIgdeS2iefgEi+ocAnyLFUFq79Goqm85827ZQabD4nwTVWykse7G"
    "Xv2vPM8s+0iDw8qs7cLFgRdOiJteROGSouBvQX7QZtN7irQZrhb4FPaK2k6A03N7HVoLt3"
    "8MvJU3AxzdUswtbobpFjTKJNNYt5Qibv199u8d7gLu3wHtTYwFF0rM+BpNA6iz3K6LQV2B"
    "YKuYgolVem3wLBlKvw2oAp8d/bQHcnNXOt8wTjsETA8i3UrkuGpQ1UgZHAOjoWWqibAS36"
    "/NgsiqbmgPX7GNhVLz2GncBRn355qdU3q3EqyfE9mn8Vmr0eRXIgDvB+++D57+Po4MQmrf"
    "0rKoB1d77oK29VXUCof9cY4irbVKDrqN50nmthqpuQccgXcMNUpAgmCHQFcDJO+4+cW51A"
    "s9s0l53Aock/Bdzud9OQvX4eUD541s0omvCWOVuRQmXZWA68JnglDC7MyuYNxUBimcVEEk"
    "HnHHA8EighnCQotXithC+oKZEt6LXGyA5ocYK3e3i3lYht1QQzohIOqsdUHGwsXkDfAN1G"
    "OcEtsTLqPMQHabjEg9vcNNsnN7a+3ziIRLjKmTkMnD+p0kCn61AyVL6UVrDft8sBbVZzm+"
    "EUZAra5mvbF/+FdZfLTzck+OFkVuVlhMmNoRYXXXELig5go+P9ofLVIl5Fvso2rDvzVNcu"
    "fQ4xgPlKCTNe76oLfplGH1WOJgDQTSJu5VDT7cC3AQSOCRt02N6Nx7mYLMlWyFXMjtYH57"
    "9uUl7BJbJ7x2eUNj15mkVKt8a1joD+bm2rpFLkmOtAGOrqhcYAPYgyw1ARg4N/k4/lRGOn"
    "xyibRASp2q7ToDxCloUHiGlupy4zPh/7WlZImb7NHIiHXBe+EFJV/VbIhN458DiOsXHz1T"
    "HnW+91Vt5/BLTaBFAnNqHbw768IZQVUcr1mnXorslCZNQFxtFuVEhF9Rdlzbm/HqaIxdFW"
    "yE8RhyJKe7hsNqI7gde6G3FeFQn5hLWfRosekgnEe91Jw3gb0Gy6wJATDOlFv77U1Sfwoa"
    "1y1XMJlBqNtFjbck4bca2vKLqQQORYf/JEt8FknneDznBYbr1ODFcfN894x2qmGcrIofjz"
    "LnWI/7N4jaHiM29haLp9SCtGlgy3JWje2VOVYwk10igyNPTHiAaRTMPK7EbAFAld6UCnxm"
    "wpLMQ/IlWpMwDKrFEBQol0l3Wx5BnoWlipk5SdA7XCtUUgrPteZgG6x2np4/hGvedytu8j"
    "jua9C7ymh8MggEIw5kUMk3mjZoJBJyUk0YUnVvGHPUkpBbd5gYTFptBNXTio8xJPtYglCS"
    "S+CJMEHbL2zjOQhvJeFXLJe3oZiN8L2Xt/q5xkcKen7jdkSQx8jHRmBuVsc58hmkaQ49Ln"
    "hg+/1YuAbZcQzKUNIM+xG1wzdSy9mBo3trlsdwcZG9NdjkWikERH/1e4RJWQftmQy1DTzB"
    "FcqIGWKztwUQzJO4xpclF5uULFxUiD72lH5ZHfKyB0dDa7AcXPcU1VwPNlEqdPAOPjIrlG"
    "Jrb56sUSeY+kiM/Dic8TmrywFvhigASFs4AlxWaOo+8zHhicxzVdsw9xWZnsvhssTMrgo/"
    "ngO86RxOgHjwJdlTCK0sMzZUjNofd3ci8fRxecWqFgNai5tAh0tR2x5FaJUxrG3qs2M+M6"
    "T2w124eEK1ztVRPlaAfaX+pwbhbjXjw//LIq4VRqaV2A05cfEMTGV/YlEbriYy5rwxnbTP"
    "KaZkbpSafkL7ymva8//TWlXJPBeZ56XpLYkBbgjhUMmw9kmc/SI8f5DId3XfmX1zFCMmXU"
    "Momg2S+2dC3h5wQEky4WJkz8o4alBLAwQUAAAAAAAAACEAPRauyggAAAAIAAAADgAAAHBj"
    "b2RlL2NvZGVUeXBlZnVuY3Rpb25QSwMEFAAAAAAAAAAhAFkvZCsGAAAABgAAABMAAABwY2"
    "9kZS9jb21wYXRpYmlsaXR5UjIwMjJhUEsBAgAAFAAAAAgAAAAhADs6JjHNAAAAZgEAABMA"
    "AAAAAAAAAQAAAAAAAAAAAFtDb250ZW50X1R5cGVzXS54bWxQSwECAAAUAAAAAAAAACEAr5"
    "Yb1voFAAD6BQAADAAAAAAAAAAAAAAAAAD+AAAAcGNvZGUvYmluYXJ5UEsBAgAAFAAAAAAA"
    "AAAhAD0WrsoIAAAACAAAAA4AAAAAAAAAAAAAAAAAIgcAAHBjb2RlL2NvZGVUeXBlUEsBAg"
    "AAFAAAAAAAAAAhAFkvZCsGAAAABgAAABMAAAAAAAAAAAAAAAAAVgcAAHBjb2RlL2NvbXBh"
    "dGliaWxpdHlQSwUGAAAAAAQABAD4AAAAjQcAAAAA"
)

SEP = "─" * 64
DIV = "━" * 64


def _human_size(nbytes: int) -> str:
    if nbytes < 1024:
        return f"{nbytes} B"
    elif nbytes < 1024 * 1024:
        return f"{nbytes / 1024:.2f} KB"
    else:
        return f"{nbytes / (1024 * 1024):.2f} MB"


def find_p_files(directory: str) -> list[str]:
    """扫描目录下所有 .p 文件，返回文件名列表。"""
    return sorted(
        f for f in os.listdir(directory)
        if f.endswith(".p") and os.path.isfile(f)
    )


def _print_file(file_name: str, file_path: str, size: int, b64_len: int):
    print(f"\n  📄 文件名      : {file_name}")
    print(f"     路径        : {file_path}")
    print(f"     文件大小    : {size:,} bytes ({_human_size(size)})")
    print(f"     Base64 长度 : {b64_len:,} 字符")


def _print_job(job: dict):
    status = job.get("status", "?")
    status_label = job.get("statusLabel", "?")
    job_id = job.get("id", "?")

    print(f"\n  📦 任务 ID          : {job_id}")
    print(f"     状态             : {status} ({status_label})")
    print(f"     会话 ID          : {job.get('sessionId', '?')}")

    source_label = job.get("sourceTypeLabel", job.get("sourceType", "?"))
    print(f"     来源类型         : {source_label}")

    total_cost = job.get("total_cost", 0)
    estimated = job.get("estimated_total_cost", 0)
    print(f"     实际费用         : {total_cost} 缘石  (预估: {estimated} 缘石)")

    zero_reason = job.get("zeroChargeReasonLabel") or job.get("zeroChargeReason")
    if zero_reason:
        print(f"     免费原因         : {zero_reason}")

    version_summary = job.get("versionSummary", {})
    if version_summary:
        parts = [f"{k}: {v} 个" for k, v in version_summary.items() if v > 0]
        if parts:
            print(f"     版本统计         : {', '.join(parts)}")

    print(f"     成功 / 失败 / 跳过 : {job.get('successCount', '?')} / {job.get('failedCount', '?')} / {job.get('skippedCount', '?')}")

    # 产物列表
    artifacts = job.get("artifacts", [])
    if artifacts:
        print(f"\n  📎 生成产物 ({len(artifacts)} 个):")
        for i, art in enumerate(artifacts, 1):
            name = art.get("outputName", "?")
            astat = art.get("status", "?")
            print(f"      {i}. {name}  [{astat}]")
            preview = art.get("previewUrl")
            if preview:
                print(f"         预览: https://pcode.948421.xyz{preview}")


def _print_quote(quote: dict):
    print(f"\n  💰 报价:")
    print(f"     文件 ID        : {quote.get('file_id', '?')}")
    print(f"     原始文件名     : {quote.get('original_name', '?')}")
    print(f"     检测版本       : {quote.get('detected_version', '?')}")
    convertible = quote.get("convertible", False)
    print(f"     可否转换       : {'✅ 是' if convertible else '❌ 否'}")
    if not convertible:
        reject = quote.get("reject_reason")
        if reject:
            print(f"     拒绝原因       : {reject}")
    print(f"     基础费用       : {quote.get('base_cost', '?')} 缘石")
    print(f"     体积费用       : {quote.get('size_cost', '?')} 缘石")
    print(f"     总费用         : {quote.get('total_cost', '?')} 缘石")


def _print_preview(preview: dict):
    masked = preview.get("maskedText")
    if not masked:
        return

    visible = preview.get("visibleCharCount", 0)
    hidden = preview.get("hiddenVisibleCharCount", 0)
    hidden_lines = preview.get("hiddenLineCount", 0)
    revealed = preview.get("revealedPerSide", 0)

    print(f"\n  🔍 脱敏预览:")
    print(f"     可见字符       : {visible} 个")
    print(f"     隐藏字符       : {hidden} 个  (分布在 {hidden_lines} 行)")
    print(f"     脱敏策略       : 文件首尾各保留 {revealed} 个可见字符")
    lines = [line for line in masked.splitlines() if line.strip() != ""]
    cleaned = "\n".join(lines)
    print(f"\n     ── 预览内容 ──")
    print(textwrap.indent(cleaned, "     "))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        chosen = sys.argv[1]
        filepath = os.path.join(script_dir, chosen)
        if not os.path.isfile(filepath):
            print(f"\n  ❌ 错误: 文件不存在 '{filepath}'")
            sys.exit(1)
        if not chosen.endswith(".p"):
            print(f"\n  ❌ 错误: 文件 '{chosen}' 不是 .p 文件")
            sys.exit(1)
        size = os.path.getsize(filepath)
        print(f"\n  🎯 指定文件: {chosen}")
        with open(filepath, "rb") as f:
            raw = f.read()
        b64_content = base64.b64encode(raw).decode("ascii")
        source = "磁盘文件"
    else:
        p_files = find_p_files(script_dir)

        if p_files:
            print(f"\n  🔎 在 '{script_dir}' 发现 {len(p_files)} 个 .p 文件:")
            for pf in p_files:
                path = os.path.join(script_dir, pf)
                print(f"      · {pf}  ({_human_size(os.path.getsize(path))})")

            chosen = random.choice(p_files)
            filepath = os.path.join(script_dir, chosen)
            size = os.path.getsize(filepath)

            print(f"\n  🎲 随机选中: {chosen}")

            with open(filepath, "rb") as f:
                raw = f.read()
            b64_content = base64.b64encode(raw).decode("ascii")
            source = "磁盘文件"
        else:
            print(f"\n  🔎 在 '{script_dir}' 没有找到 .p 文件，使用内置默认 v02.p")

            chosen = "v02.p"
            filepath = "（内置硬编码）"
            raw = base64.b64decode(_FALLBACK_V02_P_B64)
            size = len(raw)
            b64_content = _FALLBACK_V02_P_B64
            source = "内置默认"

    payload = {
        "file": {
            "name": chosen,
            "sizeBytes": size,
            "mimeType": "application/octet-stream",
            "contentBase64": f"data:application/octet-stream;base64,{b64_content}",
        }
    }

    print(f"     数据来源     : {source}")
    _print_file(chosen, filepath, size, len(b64_content))

    # ── 发送请求 ──
    print(f"\n{SEP}")
    print(f"  🚀 发送 POST 请求")
    print(f"     URL          : {API_URL}")
    print(f"     Content-Type : application/json")
    print(f"     Payload 大小 : {len(json.dumps(payload)):,} bytes")
    print(f"{SEP}")

    t0 = time.monotonic()

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=HEADERS, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status_code = resp.status
            raw_body = resp.read()
    except urllib.error.HTTPError as e:
        print(f"\n  ❌ HTTP 错误 [{e.code}]: {e.reason}")
        try:
            print(f"     响应体: {e.read().decode('utf-8', errors='replace')[:500]}")
        except Exception:
            pass
        sys.exit(2)
    except (urllib.error.URLError, TimeoutError) as e:
        msg = str(e.reason) if hasattr(e, "reason") else str(e)
        if "timed out" in msg.lower() or isinstance(e, TimeoutError):
            print(f"\n  ❌ 请求超时: {API_URL} 在 60 秒内无响应")
        else:
            print(f"\n  ❌ 请求失败: 无法连接到服务器 {API_URL}\n     原因: {msg}")
        sys.exit(2)
    except OSError as e:
        print(f"\n  ❌ 网络错误: {e}")
        sys.exit(2)

    elapsed = time.monotonic() - t0

    print(f"\n  ✅ 请求成功! 耗时 {elapsed:.2f}s")
    print(f"     HTTP 状态码 : {status_code}")
    print(f"     响应体大小   : {len(raw_body):,} bytes")

    data = json.loads(raw_body)


    # ── 1. 先打印原始 JSON ──
    print(f"\n{DIV}")
    print(f"  📋 原始 JSON 响应:")
    print(f"{DIV}")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # ── 2. 再打印结构化解释 ──
    print(f"\n{DIV}")
    print(f"  📊 响应解读:")
    print(f"{DIV}")

    # 顶层状态
    success = data.get("success", False)
    error = data.get("error")
    print(f"\n  🏷️  顶层状态:")
    print(f"     业务成功     : {'✅ 是' if success else '❌ 否'}")
    if error:
        print(f"     业务错误     : {error}")

    # 文件信息
    file_info = data.get("file", {})
    if file_info:
        print(f"\n  📄 上传确认:")
        print(f"     文件名       : {file_info.get('name', '?')}")
        print(f"     大小         : {file_info.get('sizeBytes', '?'):,} bytes")
        print(f"     检测版本     : {file_info.get('detectedVersion', '?')}")

    # 报价
    quote = data.get("quote")
    if quote:
        _print_quote(quote)

    # 任务详情
    job = data.get("job")
    if job:
        _print_job(job)

    # 预览
    preview = data.get("preview")
    if preview:
        _print_preview(preview)

    print(f"\n{DIV}")
    print(f"  🏁 脚本执行完毕")
    print(f"{DIV}\n")


if __name__ == "__main__":
    main()
