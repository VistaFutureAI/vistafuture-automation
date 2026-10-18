
import asyncio
import random
import shutil
import subprocess
import textwrap
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

CHANNEL = "VistaFuture"
VOICE = "en-US-AndrewNeural"
OUTPUT = Path("output")

TOPICS = [
    "The Future of Artificial Intelligence",
    "How Technology Could Change Cities by 2050",
    "The Future of Space Exploration",
    "Robots and the Future of Human Life",
    "Amazing Technologies That Could Change Our World",
    "How Science Is Shaping Tomorrow"
]

def make_script(topic):
    sections = [
        ("INTRODUCTION",
         f"Welcome to {CHANNEL}. Today, we explore {topic}. "
         "Technology is changing how people live, work, communicate, "
         "and understand the universe. In this episode, we will look "
         "at the possibilities, the science behind the ideas, and "
         "the challenges that may shape the years ahead."),

        ("WHY IT MATTERS",
         f"Why should we care about {topic}? New discoveries can "
         "create opportunities that once seemed impossible. They may "
         "help people solve difficult problems, use resources more "
         "efficiently, and discover new ways to work together. But "
         "progress is not only about machines. It is also about the "
         "people who design, use, and live with these technologies."),

        ("HOW PROGRESS HAPPENS",
         "Most important breakthroughs do not happen overnight. "
         "Researchers ask questions, test ideas, study results, "
         "and improve their designs. Engineers turn scientific "
         "knowledge into practical tools. Some experiments fail, "
         "while others reveal unexpected possibilities. This process "
         "takes time, investment, teamwork, and careful testing. "
         "That is why bold predictions should always be treated "
         "as possibilities rather than guaranteed outcomes."),

        ("POSSIBLE BENEFITS",
         f"In the future, advances connected with {topic} could "
         "help people make better decisions, communicate across "
         "distances, or complete complex tasks more efficiently. "
         "Some applications may improve education, scientific "
         "research, transportation, or access to information. "
         "The real benefits will depend on whether these tools "
         "are affordable, reliable, useful, and available to "
         "different communities around the world."),

        ("CHALLENGES TO SOLVE",
         "Every new technology brings important questions. How "
         "much will it cost? Can it be trusted? What happens "
         "when something goes wrong? People may also need to "
         "consider privacy, safety, energy use, and the effect "
         "on jobs. Scientists, businesses, governments, and "
         "communities will need to work together to reduce risks "
         "and make responsible choices."),

        ("WHAT COMES NEXT",
         f"The next chapter of {topic} will depend on discoveries "
         "that have not happened yet. Researchers may find better "
         "materials, smarter methods, or entirely new approaches. "
         "Some ideas will become useful products, while others "
         "may remain experiments. Following credible research "
         "and looking carefully at the evidence helps us separate "
         "real progress from exaggerated headlines."),

        ("FINAL THOUGHTS",
         "The future is not something we can predict perfectly. "
         "It is something people help create through curiosity, "
         "learning, and decisions made today. If you enjoy "
         "discovering ideas about science and tomorrow's world, "
         "subscribe to VistaFuture for more explorations. "
         "Thanks for watching, and we will see you in the next episode.")
    ]
    return topic, sections

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def make_slide(title, section, index):
    image = Image.new("RGB", (1280, 720), (10, 18, 42))
    draw = ImageDraw.Draw(image)

    # Simple original abstract technology artwork
    for i in range(8):
        x = 850 + i * 42
        draw.ellipse(
            (x, 90 + i * 18, x + 260, 350 + i * 18),
            outline=(20, 95 + i * 10, 150 + i * 8),
            width=3
        )

    draw.rectangle((65, 90, 75, 625), fill=(45, 190, 220))
    draw.text((110, 110), CHANNEL.upper(),
              font=get_font(30, True), fill=(80, 220, 240))

    y = 230
    for line in textwrap.wrap(title, width=27)[:3]:
        draw.text((110, y), line,
                  font=get_font(54, True), fill="white")
        y += 75

    draw.text((110, 565), section,
              font=get_font(27), fill=(160, 200, 225))
    draw.text((110, 635), f"FUTURE • SCIENCE • TECHNOLOGY",
              font=get_font(20), fill=(100, 170, 200))

    path = OUTPUT / f"slide_{index:02d}.png"
    image.save(path)
    return path

async def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and ffprobe must be installed.")

    OUTPUT.mkdir(exist_ok=True)
    topic, sections = make_script(random.choice(TOPICS))
    full_text = "\n\n".join(
        f"{heading}\n{text}" for heading, text in sections
    )

    (OUTPUT / "script.txt").write_text(
        f"{topic}\n\n{full_text}", encoding="utf-8"
    )

    audio_path = OUTPUT / "narration.mp3"
    communicate = edge_tts.Communicate(
        full_text, VOICE, rate="-5%"
    )
    await communicate.save(str(audio_path))

    slides = []
    for i, (heading, _) in enumerate(sections):
        slides.append(make_slide(topic, heading, i))

    probe = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         str(audio_path)],
        capture_output=True, text=True, check=True
    )
    audio_seconds = float(probe.stdout.strip())

    # Allocate slide time according to each narration section.
    word_counts = [len(text.split()) for _, text in sections]
    total_words = sum(word_counts)
    concat_file = OUTPUT / "slides.txt"

    with concat_file.open("w", encoding="utf-8") as f:
        for slide, count in zip(slides, word_counts):
            f.write(f"file '{slide.resolve()}'\n")
            f.write(
                f"duration {audio_seconds * count / total_words:.3f}\n"
            )
        f.write(f"file '{slides[-1].resolve()}'\n")

    video_path = OUTPUT / "vistafuture.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "scale=1280:720,format=yuv420p",
        "-r", "24",
        "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(video_path)
    ], check=True)

    print(f"Topic: {topic}")
    print(f"Video length: {audio_seconds / 60:.1f} minutes")
    print(f"Video saved: {video_path}")

if __name__ == "__main__":
    asyncio.run(main())
