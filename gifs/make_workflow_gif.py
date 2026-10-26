"""Make gifs/workflow.gif: examples/python_workflow run in Python (terminal
output and the interactive figure), then transpiled to C, with the
computation times. Everything shown comes from actual runs.

usage: python gifs/make_workflow_gif.py

Needs prometeo, matplotlib with a GUI backend (TkAgg) and a display, and
Pillow. The Python run is driven by a harness that answers as a terminal and,
instead of waiting for the window to be closed, saves what the window shows
while the slider moves.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, 'examples', 'python_workflow')
OUT = os.path.join(ROOT, 'gifs', 'workflow.gif')

W, H = 960, 600
FONT_SIZE, LINE = 14, 19
TOP, LEFT = 44, 18
COLORS = {
    'bg': (30, 30, 46), 'bar': (49, 50, 68), 'fg': (205, 214, 244),
    'prompt': (166, 227, 161), 'python': (137, 220, 235), 'prometeo': (249, 226, 175),
    'dim': (127, 132, 156), 'time': (243, 139, 168),
}

HARNESS = r'''
import gc, os, sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

FRAMES = sys.argv[1]
FIGURE = []

def show():
    # instead of waiting for the window to be closed: keep the figure, whose
    # frames (moving the slider) are saved after the program ends, so that
    # the time it prints does not include them
    slider = [o for o in gc.get_objects() if isinstance(o, Slider)][0]
    FIGURE.append((plt.gcf(), slider))

plt.show = show
sys.stdout.isatty = lambda: True
sys.argv = ['pmt', 'cartpole_workflow.py']
from prometeo.cmdline.pmt import pmt_main
pmt_main()
fig, slider = FIGURE[0]
for i, k in enumerate(list(range(0, 60, 2)) + [59]):
    slider.set_val(k)
    fig.savefig(os.path.join(FRAMES, 'figure_%03d.png' % i), dpi=72)
'''


def font(bold=False):
    name = 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'
    for d in ('/usr/share/fonts/truetype/dejavu', '/Library/Fonts', ''):
        try:
            return ImageFont.truetype(os.path.join(d, name), FONT_SIZE)
        except OSError:
            pass
    return ImageFont.load_default()


REGULAR, BOLD = font(), font(bold=True)


def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True)
    if proc.returncode != 0:
        sys.exit('{} failed:\n{}'.format(' '.join(cmd), proc.stdout))
    return proc.stdout


def output_lines(text):
    """Lines of a terminal output, without ANSI codes and repeated blank lines."""
    lines = []
    for line in re.sub(r'\x1b\[[0-9;]*m', '', text).splitlines():
        if line.strip() or (lines and lines[-1].strip()):
            lines.append(line.rstrip())
    return lines


def style(line):
    if line.startswith('$ '):
        return 'prompt'
    if line.startswith('[python]'):
        return 'python'
    if 'prometeo:' in line:
        return 'prometeo'
    if 'xecution time' in line or 'total time' in line:
        return 'time'
    if 'bytes aligned' in line:
        return 'dim'
    return 'fg'


def window(draw, box, title):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, 10, fill=COLORS['bg'], outline=(88, 91, 112))
    draw.rounded_rectangle((x0, y0, x1, y0 + 30), 10, fill=COLORS['bar'])
    draw.rectangle((x0, y0 + 20, x1, y0 + 30), fill=COLORS['bar'])
    for i, c in enumerate([(243, 139, 168), (249, 226, 175), (166, 227, 161)]):
        draw.ellipse((x0 + 12 + 20 * i, y0 + 9, x0 + 24 + 20 * i, y0 + 21), fill=c)
    draw.text(((x0 + x1) // 2, y0 + 15), title, fill=COLORS['dim'], font=REGULAR, anchor='mm')


def terminal(lines, cursor=False):
    img = Image.new('RGB', (W, H), (17, 17, 27))
    draw = ImageDraw.Draw(img)
    window(draw, (6, 6, W - 6, H - 6), 'prometeo/examples/python_workflow')
    rows = (H - TOP - 12) // LINE
    shown = lines[-rows:]
    for i, line in enumerate(shown):
        y = TOP + i * LINE
        s = style(line)
        if s == 'prompt':
            draw.text((LEFT, y), '$', fill=COLORS['prompt'], font=BOLD)
            draw.text((LEFT + 2 * draw.textlength(' ', font=REGULAR), y), line[2:],
                fill=COLORS['fg'], font=BOLD)
        else:
            draw.text((LEFT, y), line, fill=COLORS[s], font=BOLD if s == 'prometeo' else REGULAR)
    if cursor:
        last = shown[-1] if shown else ''
        x = LEFT + draw.textlength(last, font=REGULAR)
        y = TOP + (len(shown) - 1) * LINE
        draw.rectangle((x + 1, y + 1, x + 8, y + LINE - 3), fill=COLORS['fg'])
    return img


def with_figure(background, figure):
    img = background.copy()
    draw = ImageDraw.Draw(img)
    scale = (H - 70) / figure.height
    fig = figure.resize((int(figure.width * scale), int(figure.height * scale)), Image.LANCZOS)
    x0, y0 = W - fig.width - 40, 22
    window(draw, (x0 - 4, y0, x0 + fig.width + 4, y0 + fig.height + 36), 'Figure 1')
    img.paste(fig, (x0, y0 + 32))
    return img


def summary(background, t_python, t_c):
    img = background.copy()
    draw = ImageDraw.Draw(img, 'RGBA')
    draw.rectangle((0, 0, W, H), fill=(17, 17, 27, 200))
    box = (W // 2 - 330, H // 2 - 140, W // 2 + 330, H // 2 + 150)
    window(draw, box, 'same program, same numbers')
    big = ImageFont.truetype(REGULAR.path, 26) if hasattr(REGULAR, 'path') else REGULAR
    x, y = box[0] + 40, box[1] + 60
    rows = [('Python', '{:.2f} s'.format(t_python), COLORS['python']),
        ('transpiled C', '{:.2f} ms'.format(t_c * 1e3), COLORS['prompt'])]
    for label, value, color in rows:
        draw.text((x, y), label, fill=COLORS['fg'], font=big)
        draw.text((box[2] - 40, y), value, fill=color, font=big, anchor='ra')
        y += 46
    draw.text((x, y + 6), '{:.0f}x faster'.format(t_python / t_c), fill=COLORS['prometeo'], font=big)
    note = ['Gauss-Newton SQP, closed-loop MPC with 60 steps, without',
        'the Python-only checks and plots (best of several runs).',
        'Both runs print the same numbers.']
    for i, line in enumerate(note):
        draw.text((x, y + 60 + i * LINE), line, fill=COLORS['dim'], font=REGULAR)
    return img


def main():
    work = tempfile.mkdtemp()
    example = os.path.join(work, 'python_workflow')
    shutil.copytree(EXAMPLE, example, ignore=shutil.ignore_patterns('__pmt_cache__', '*.png'))
    frames_dir = os.path.join(work, 'frames')
    os.makedirs(frames_dir)
    with open(os.path.join(example, 'harness.py'), 'w') as f:
        f.write(HARNESS)

    py_out = output_lines(run([sys.executable, 'harness.py', frames_dir], example))
    c_out = output_lines(run([sys.executable, '-m', 'prometeo', 'cartpole_workflow.py',
        '--cgen=True'], example))

    # timings without the checks and plots: the pure blocks in functions removed
    source = open(os.path.join(example, 'cartpole_workflow.py')).read()
    lines, inside = [], False
    for line in source.splitlines():
        if line.startswith(' ') and line.strip() == '# pure >':
            inside = True
        lines.append('' if inside else line)
        if inside and line.strip() == '# pure <':
            inside = False
    with open(os.path.join(example, 'timing.py'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    # best of several runs: single runs are noisy
    t_python = min(float(re.search(r'Execution time = ([0-9.]+)', run(
        [sys.executable, '-m', 'prometeo', 'timing.py'], example)).group(1)) for _ in range(3))
    binary = os.path.join(example, '__pmt_cache__', 'cartpole_workflow')
    runs = ['\n'.join(c_out)] + [run([binary], os.path.dirname(binary)) for _ in range(10)]
    t_c = min(float(re.search(r'execution time:([0-9.]+)', r).group(1)) for r in runs)
    same = [l for l in c_out if l.startswith(('first solve', 'closed loop'))]
    assert all(l in py_out for l in same), (same, py_out)

    frames, durations = [], []

    def add(img, ms):
        frames.append(img)
        durations.append(ms)

    def type_command(lines, command):
        for i in range(0, len(command) + 1, 2):
            add(terminal(lines + ['$ ' + command[:i]], cursor=True), 45)
        add(terminal(lines + ['$ ' + command]), 400)
        return lines + ['$ ' + command]

    lines = type_command([], 'pmt cartpole_workflow.py')
    figures = sorted(os.listdir(frames_dir))
    for line in py_out:
        lines = lines + [line]
        add(terminal(lines), 120 if line.strip() else 40)
        if line.startswith('[python] close the figure'):
            background = terminal(lines)
            for i, name in enumerate(figures):
                figure = Image.open(os.path.join(frames_dir, name)).convert('RGB')
                add(with_figure(background, figure), 1500 if i == 0 else 160)
            durations[-1] = 1500
    durations[-1] = 1200
    lines = type_command(lines + [''], 'pmt cartpole_workflow.py --cgen=True')
    for line in c_out:
        lines = lines + [line]
        add(terminal(lines), 110 if line.strip() else 30)
    durations[-1] = 1500
    add(summary(terminal(lines), t_python, t_c), 5000)

    palette = [f.convert('P', palette=Image.ADAPTIVE, colors=128) for f in frames]
    palette[0].save(OUT, save_all=True, append_images=palette[1:], duration=durations,
        loop=0, optimize=True)
    print('{}: {} frames, {:.1f} s, {:.0f} kB; Python {:.2f} s, C {:.2f} ms'.format(
        OUT, len(frames), sum(durations) / 1e3, os.path.getsize(OUT) / 1e3, t_python, t_c * 1e3))
    shutil.rmtree(work)


if __name__ == '__main__':
    main()
