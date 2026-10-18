
from pathlib import Path
from datetime import datetime
import random

CHANNEL = "VistaFuture"

TOPICS = [
    "What Will Cities Look Like in 2050?",
    "5 Future Technologies That Could Change Human Life",
    "Could Artificial Intelligence Discover New Planets?",
    "What Happens If Humans Live on Mars?",
    "How Robots Could Transform Everyday Life",
    "The Future of Space Exploration",
    "Technologies That May Change the World"
]

def main():
    topic = random.choice(TOPICS)

    script = f"""
Welcome to {CHANNEL}, where we explore the science
and technology shaping tomorrow.

Today, we are exploring: {topic}

Imagine a world where technology changes the way
we live, work, and understand the universe.

Scientists and engineers are developing new ideas
that could transform everyday life. Some technologies
are still experimental, while others are already
changing the world around us.

The most important question is not just what
technology can do, but how people will use it
responsibly.

As research continues, the future may bring
unexpected discoveries, new opportunities,
and challenges we must solve together.

Remember, predictions about the future are not
guarantees. Real progress depends on science,
experimentation, and human decisions.

Thanks for watching {CHANNEL}.
Subscribe for more discoveries about science,
artificial intelligence, and future technology.
"""

    output = Path("output")
    output.mkdir(exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d")
    filename = output / f"script-{date}.txt"
    filename.write_text(
        f"TITLE: {topic}\\n\\n{script.strip()}",
        encoding="utf-8"
    )

    print(f"Script saved to {filename}")

if __name__ == "__main__":
    main()
