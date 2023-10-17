import copy
import math
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))


class Countdown(Enum):
    NO_COUNTDOWN = 0
    NORMAL = 1
    HALF = 2
    DOUBLE = 3


class SampleSet(Enum):
    NORMAL = "Normal"
    SOFT = "Soft"
    DRUM = "Drum"


class GameMode(Enum):
    STANDARD = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3


class OverlayPosition(Enum):
    NO_CHANGE = "NoChange"
    """use skin setting"""

    BELOW = "Below"
    """draw overlays under numbers"""

    ABOVE = "Above"
    """draw overlays on top of numbers"""


@dataclass
class General:
    audio_filename: str = ""
    """Location of the audio file relative to the current folder"""

    audio_lead_in: int = 0
    """Milliseconds of silence before the audio starts playing"""

    audio_hash: str = ""
    """Deprecated"""

    preview_time: int = -1
    """Time in milliseconds when the audio preview should start"""

    countdown: Countdown = Countdown.NORMAL
    """Speed of the countdown before the first hit object"""

    sample_set: SampleSet = SampleSet.NORMAL
    """Sample set that will be used if timing points do not override it (Normal, Soft, Drum)"""

    stack_leniency: Decimal = Decimal("0.7")
    """Multiplier for the threshold in time where hit objects placed close together stack (0–1)"""

    mode: GameMode = GameMode.STANDARD
    """Game mode"""

    letterbox_in_breaks: bool = False
    """Whether or not breaks have a letterboxing effect"""

    story_fire_in_front: bool = True
    """Deprecated"""

    use_skin_sprites: bool = False
    """Whether or not the storyboard can use the user's skin images"""

    always_show_playfield: bool = False
    """Deprecated"""

    overlay_position: str = OverlayPosition.NO_CHANGE
    """Draw order of hit circle overlays compared to hit numbers"""

    skin_preference: str = ""
    """Preferred skin to use during gameplay"""

    epilepsy_warning: bool = False
    """Whether or not a warning about flashing colours should be shown at the beginning of the map"""

    countdown_offset: int = 0
    """Time in beats that the countdown starts before the first hit object"""

    special_style: bool = False
    """Whether or not the "N+1" style key layout is used for osu!mania"""

    widescreen_storyboard: bool = False
    """Whether or not the storyboard allows widescreen viewing"""

    samples_match_playback_rate: bool = False
    """Whether or not sound samples will change rate when playing with speed-changing mods"""


@dataclass
class Editor:
    distance_spacing: Decimal = Decimal(1)
    """Distance snap multiplier"""

    beat_divisor: int = 4
    """Beat snap divisor"""

    grid_size: int = 64
    """Grid size"""

    timeline_zoom: Decimal = Decimal()
    """Scale factor for the object timeline"""

    bookmarks: list[int] = default_field([])
    """Time in milliseconds of bookmarks"""


@dataclass
class Metadata:
    title: str = ""
    """Romanised song title"""

    title_unicode: str = ""
    """Song title"""

    artist: str = ""
    """Romanised song artist"""

    artist_unicode: str = ""
    """Song artist"""

    creator: str = ""
    """Beatmap creator"""

    version: str = ""
    """Difficulty name"""

    source: str = ""
    """Original media the song was produced for"""

    tags: list[str] = default_field([])
    """separated list of strings"""

    beatmap_id: int = -1
    """Difficulty ID"""

    beatmap_set_id: int = -1
    """Beatmap ID"""


@dataclass
class Difficulty:
    hp_drain_rate: Decimal = Decimal(5)
    """HP setting (0–10)"""

    circle_size: Decimal = Decimal(5)
    """CS setting (0–10)"""

    overall_difficulty: Decimal = Decimal(5)
    """OD setting (0–10)"""

    approach_rate: Decimal = Decimal(5)
    """AR setting (0–10)"""

    slider_multiplier: Decimal = Decimal(5)
    """Base slider velocity in hundreds of osu! pixels per beat"""

    slider_tick_rate: Decimal = Decimal(5)
    """Amount of slider ticks per beat"""


@dataclass
class Event:
    event_type: int | str
    """Type of the event. Some events may be referred to by either a name or a number."""

    start_time: int
    """Start time of the event, in milliseconds from the beginning of the beatmap's audio.
    For events that do not use a start time, the default is 0."""


@dataclass
class Background(Event):
    event_type = 0  # Background
    filename: str
    """Location of the background image relative to the beatmap directory.
    Double quotes are usually included surrounding the filename, but they are not required."""

    x_offset: int
    """Offset in osu! pixels from the centre of the screen."""

    y_offset: int
    """Offset in osu! pixels from the centre of the screen."""


@dataclass
class Video(Event):
    event_type = 1  # Video
    filename: str
    """Location of the background video relative to the beatmap directory.
    Double quotes are usually included surrounding the filename, but they are not required."""

    x_offset: int
    """Offset in osu! pixels from the centre of the screen."""

    y_offset: int
    """Offset in osu! pixels from the centre of the screen."""


@dataclass
class Break(Event):
    event_type = 2  # Break
    start_time: int
    """End time of the break, in milliseconds from the beginning of the beatmap's audio."""


@dataclass
class Events:
    events: list[Event] = default_field([])


class TimingPointSampleSet(Enum):
    DEFAULT = 0
    NORMAL = 1
    SOFT = 2
    DRUM = 3


def create_effects(x):
    kiai_time = bool((x << 0) & 1)
    bar_line = bool((x << 3) & 1)

    return Effects(kiai_time, bar_line)


@dataclass
class Effects:
    kiai_time: bool
    """Whether or not kiai time is enabled"""

    bar_line: bool
    """Whether or not the first barline is omitted in osu!taiko and osu!mania"""


@dataclass
class TimingPoint:
    time: Decimal  # should be int but some beatmaps have decimals
    """Start time of the timing section, in milliseconds from the beginning of the beatmap's audio. The end of the 
    timing section is the next timing point's time (or never, if this is the last timing point)."""

    meter: int
    """Amount of beats in a measure. Inherited timing points ignore this property."""

    sample_set: int
    """Default sample set for hit objects."""

    sample_index: int
    """Custom sample index for hit objects. 0 indicates osu!'s default hitsounds."""

    volume: int
    """Volume percentage for hit objects."""

    uninherited: bool
    """Whether or not the timing point is uninherited."""

    effects: Effects
    """Bit flags that give the timing point extra effects. See the effects section."""

    beat_duration: Decimal = Decimal()
    """The duration of a beat, in milliseconds."""

    sv_multiplier: Decimal = Decimal(1)
    """A negative inverse slider velocity multiplier, as a percentage.
    For example, -50 would make all sliders in this timing section twice as fast as SliderMultiplier."""


@dataclass
class Colors:
    colors: list[tuple[int, ...]] = default_field([])
    """Combo Colors"""

    slider_track_override: tuple[int, int, int] | None = None
    """Additive slider track colour"""

    slider_border: tuple[int, int, int] | None = None
    """Slider border colour"""


class HitObjectType(Enum):
    HIT_CIRCLE = 2 ** 0
    """hit circle"""

    SLIDER = 2 ** 1
    """slider"""

    SPINNER = 2 ** 3
    """spinner"""

    HOLD_NOTE = 2 ** 7
    """osu!mania hold note"""


@dataclass
class HitSound:
    normal: bool
    whistle: bool
    finish: bool
    clap: bool


def create_hit_sound(x: int):
    normal = bool((x << 0) & 1)
    whistle = bool((x << 1) & 1)
    finish = bool((x << 2) & 1)
    clap = bool((x << 3) & 1)

    return HitSound(normal, whistle, finish, clap)


def create_hit_sample(x: str):
    normal_set, addition_set, index, volume, filename = x.split(":")

    normal_set = int(normal_set)
    addition_set = int(addition_set)
    index = int(index)
    volume = int(volume)

    return HitSample(TimingPointSampleSet(normal_set), TimingPointSampleSet(addition_set), index, volume, filename)


@dataclass
class HitSample:
    normal_set: TimingPointSampleSet = default_field(TimingPointSampleSet.DEFAULT)
    """Sample set of the normal sound."""

    addition_set: TimingPointSampleSet = default_field(TimingPointSampleSet.DEFAULT)
    """Sample set of the whistle, finish, and clap sounds."""

    index: int = 0
    """Index of the sample. If this is 0, the timing point's sample index will be used instead."""

    volume: int = 0
    """Volume of the sample from 1 to 100. If this is 0, the timing point's volume will be used instead."""

    filename: str = ""
    """Custom filename of the addition sound."""


@dataclass
class HitObject:
    x: int
    """Position in osu! pixels of the object."""

    y: int
    """Position in osu! pixels of the object."""

    time: int
    """Time when the object is to be hit, in milliseconds from the beginning of the beatmap's audio."""

    type: HitObjectType
    """type of the object"""

    hit_sound: HitSound
    """Hitsound additions applied to the object"""

    new_combo: bool
    """Whether or not the object is the start of a new combo"""

    combo_to_skip: int
    """How many combo colours to skip, a practice referred to as "colour hax".
    Only relevant if the object starts a new combo."""

    hit_sample: HitSample
    """Information about which samples are played when the object is hit."""


@dataclass
class HitCircle(HitObject):
    pass


class CurveType(Enum):
    BEZIER = "B"
    """bézier"""

    CATMULL = "C"
    """centripetal catmull-rom"""

    LINEAR = "L"
    """linear"""

    PERFECT = "P"
    """perfect circle"""


@dataclass
class Curve:
    curve_type: CurveType
    """Type of curve"""

    curve_points: list[tuple[int, int]]
    """Anchor points used to construct the curve"""


@dataclass
class Slider(HitObject):
    curves: list[Curve]
    """Curves used to construct the slider"""

    slides: int
    """Amount of times the player has to follow the slider's curve back-and-forth before the slider is complete. It 
    can also be interpreted as the repeat count plus one."""

    length: Decimal
    """Visual length in osu! pixels of the slider."""

    edge_sounds: list[int]
    """Hitsounds that play when hitting edges of the slider's curve. The first sound is the one that plays when the 
    slider is first clicked, and the last sound is the one that plays when the slider's end is hit."""

    edge_sets: list[tuple[TimingPointSampleSet, TimingPointSampleSet]]
    """Sample sets used for the edgeSounds. Each set is in the format normalSet:additionSet, with the same meaning as 
    in the hitsounds section."""

    end_time: int = 0  # to be populated after

    duration: Decimal = 0  # to be populated after

    timing_point: TimingPoint = None  # to be populated after


@dataclass
class Spinner(HitObject):
    end_time: int


@dataclass
class Beatmap:
    general: General = default_field(General())
    """General information about the beatmap"""

    editor: Editor = default_field(Editor())
    """Saved settings for the beatmap editor"""

    metadata: Metadata = default_field(Metadata())
    """Information used to identify the beatmap"""

    difficulty: Difficulty = default_field(Difficulty())
    """Difficulty settings"""

    events: Events = default_field(Events())
    """Beatmap and storyboard graphic events"""

    timing_points: list[TimingPoint] = default_field([])
    """Timing and control points"""

    colors: Colors = default_field(Colors())
    """Combo and skin colours"""

    hit_objects: list[HitObject] = default_field([])
    """Hit objects	Comma-separated lists"""


class Section(Enum):
    GENERAL = 0,
    EDITOR = 1,
    METADATA = 2,
    DIFFICULTY = 3,
    EVENTS = 4,
    TIMING_POINTS = 5,
    COLORS = 6,
    HIT_OBJECTS = 7,


def populate_timing_point_properties(beatmap: Beatmap):
    """Sets beat length of inherited timing points"""
    timing_points = iter(sorted(beatmap.timing_points, key=lambda x: x.time))
    last_beat_duration = 0

    for timing_point in timing_points:
        if timing_point.uninherited:
            last_beat_duration = timing_point.beat_duration
        else:
            timing_point.beat_duration = last_beat_duration


def populate_slider_properties(beatmap: Beatmap):
    timing_points = sorted(beatmap.timing_points, key=lambda x: x.time)
    i = 0

    timing_point = timing_points[i]
    next_time = timing_points[i + 1].time

    hit_objects = sorted(beatmap.hit_objects, key=lambda x: x.time)
    for hit_object in hit_objects:
        if hit_object.type == HitObjectType.SLIDER:
            hit_object: Slider

            while hit_object.time >= next_time:
                i += 1

                timing_point = timing_points[i]
                if i + 1 < len(timing_points):
                    next_time = timing_points[i + 1].time
                else:
                    next_time = math.inf

            duration = timing_point.beat_duration * hit_object.slides * hit_object.length / \
                       (timing_point.sv_multiplier * 100 * beatmap.difficulty.slider_multiplier)

            hit_object.end_time = hit_object.time + duration
            hit_object.duration = duration
            hit_object.timing_point = timing_point


def load(filename: str):
    beatmap = Beatmap()

    with open(filename) as file:
        lines = file.readlines()

    section = None

    for line in lines:
        line = line.rstrip()
        if len(line) == 0:
            continue

        if line.startswith("["):  # new section
            section_text = line[1: -1]
            if section_text == "General":
                section = Section.GENERAL
            elif section_text == "Editor":
                section = Section.EDITOR
            elif section_text == "Metadata":
                section = Section.METADATA
            elif section_text == "Difficulty":
                section = Section.DIFFICULTY
            elif section_text == "Events":
                section = Section.EVENTS
            elif section_text == "TimingPoints":
                section = Section.TIMING_POINTS
            elif section_text == "Colours":
                section = Section.COLORS
            elif section_text == "HitObjects":
                section = Section.HIT_OBJECTS
            continue

        if section == Section.GENERAL:
            key, value = line.split(":")

            key = key.strip()
            value = value.strip()

            if key == "AudioFilename":
                beatmap.general.audio_filename = value
            elif key == "AudioLeadIn":
                beatmap.general.audio_lead_in = int(value)
            elif key == "AudioHash":
                beatmap.general.audio_hash = value
            elif key == "PreviewTime":
                beatmap.general.preview_time = int(value)
            elif key == "Countdown":
                beatmap.general.countdown = int(value)
            elif key == "SampleSet":
                beatmap.general.sample_set = value
            elif key == "StackLeniency":
                beatmap.general.stack_leniency = Decimal(value)
            elif key == "Mode":
                beatmap.general.mode = int(value)
            elif key == "LetterboxInBreaks":
                beatmap.general.letterbox_in_breaks = bool(int(value))
            elif key == "StoryFireInFront":
                beatmap.general.story_fire_in_front = bool(int(value))
            elif key == "UseSkinSprites":
                beatmap.general.use_skin_sprites = bool(int(value))
            elif key == "AlwaysShowPlayfield":
                beatmap.general.always_show_playfield = bool(int(value))
            elif key == "OverlayPosition":
                beatmap.general.overlay_position = str(value)
            elif key == "SkinPreference":
                beatmap.general.skin_preference = str(value)
            elif key == "EpilepsyWarning":
                beatmap.general.epilepsy_warning = bool(int(value))
            elif key == "CountdownOffset":
                beatmap.general.countdown_offset = int(value)
            elif key == "SpecialStyle":
                beatmap.general.special_style = bool(int(value))
            elif key == "WidescreenStoryboard":
                beatmap.general.widescreen_storyboard = bool(int(value))
            elif key == "SamplesMatchPlaybackRate":
                beatmap.general.samples_match_playback_rate = bool(int(value))
        elif section == Section.EDITOR:
            key, value = line.split(":")

            if key == "DistanceSpacing":
                beatmap.editor.distance_spacing = Decimal(value)
            if key == "BeatDivisor":
                beatmap.editor.beat_divisor = int(value)
            if key == "GridSize":
                beatmap.editor.grid_size = int(value)
            if key == "TimelineZoom":
                beatmap.editor.timeline_zoom = Decimal(value)
            if key == "Bookmarks":
                beatmap.editor.bookmarks = [int(x) for x in value.split(",")]
        elif section == Section.METADATA:
            key, value = line.split(":", maxsplit=1)  # metadata might have more than one colon

            key = key.strip()
            value = value.strip()

            if key == "Title":
                beatmap.metadata.title = value
            if key == "TitleUnicode":
                beatmap.metadata.title_unicode = value
            if key == "Artist":
                beatmap.metadata.artist = value
            if key == "ArtistUnicode":
                beatmap.metadata.artist_unicode = value
            if key == "Creator":
                beatmap.metadata.creator = value
            if key == "Version":
                beatmap.metadata.version = value
            if key == "Source":
                beatmap.metadata.source = value
            if key == "Tags":
                beatmap.metadata.tags = value.split(" ")
            if key == "BeatmapID":
                beatmap.metadata.beatmap_id = int(value)
            if key == "BeatmapSetID":
                beatmap.metadata.beatmap_set_id = int(value)
        elif section == Section.DIFFICULTY:
            key, value = line.split(":")

            if key == "HPDrainRate":
                beatmap.difficulty.hp_drain_rate = Decimal(value)
            if key == "CircleSize":
                beatmap.difficulty.circle_size = Decimal(value)
            if key == "OverallDifficulty":
                beatmap.difficulty.overall_difficulty = Decimal(value)
            if key == "ApproachRate":
                beatmap.difficulty.approach_rate = Decimal(value)
            if key == "SliderMultiplier":
                beatmap.difficulty.slider_multiplier = Decimal(value)
            if key == "SliderTickRate":
                beatmap.difficulty.slider_tick_rate = Decimal(value)
        elif section == Section.EVENTS:
            pass
        elif section == Section.TIMING_POINTS:
            time, beat_length, meter, sample_set, sample_index, volume, uninherited, effects = line.split(
                ",")
            time = Decimal(time)
            beat_length = Decimal(beat_length)
            meter = int(meter)
            sample_set = int(sample_set)
            sample_index = int(sample_index)
            volume = int(volume)
            uninherited = bool(int(uninherited))
            effects = create_effects(int(effects))

            if uninherited:
                timing_point = TimingPoint(
                    time, meter, sample_set, sample_index, volume, uninherited, effects, beat_length)
            else:
                timing_point = TimingPoint(
                    time, meter, sample_set, sample_index, volume, uninherited, effects, Decimal(), -100 / beat_length)

            beatmap.timing_points.append(timing_point)
        elif section == Section.COLORS:
            key, value = line.split(":")

            key = key.strip()
            value = value.strip()

            color = tuple([int(x) for x in value.split(",")])

            if key.startswith("Combo"):
                # TODO actually take this into account
                _color_index = int(key[5:])
                beatmap.colors.colors.append(color)
            elif key == "SliderTrackOverride":
                beatmap.colors.slider_track_override = color
            elif key == "SliderBorder":
                beatmap.colors.slider_border = color
        elif section == Section.HIT_OBJECTS:
            # object_params may include hit_sample
            x, y, start_time, object_type_flag, hit_sound, * \
                object_params = line.split(",")

            x = int(x)
            y = int(y)
            start_time = int(start_time)
            object_type_flag = int(object_type_flag)
            # bits 0 (hit circle), 1 (slider), 3 (spinner), 7 (mania hold note)
            object_type = HitObjectType(object_type_flag & 139)
            new_combo = bool(object_type_flag & (1 << 2))
            combo_to_skip = (object_type_flag << 4) & 7
            hit_sound = int(hit_sound)

            if object_type == HitObjectType.HIT_CIRCLE:  # should i use & instead of ==
                if len(object_params) > 0:
                    hit_sample = create_hit_sample(object_params[-1])
                else:
                    hit_sample = HitSample()

                beatmap.hit_objects.append(HitCircle(
                    x, y, start_time, object_type, create_hit_sound(hit_sound), new_combo, combo_to_skip, hit_sample))
            elif object_type == HitObjectType.SLIDER:
                curves, slides, length, edge_sounds, edge_sets_str, *hit_sample = object_params
                curve_type, *curve_points_str = curves.split("|")

                curve_type = CurveType(curve_type)

                curve_points = []
                for curve_point in curve_points_str:
                    point_x, point_y = curve_point.split(":")

                    point_x = int(point_x)
                    point_y = int(point_y)

                    curve_points.append((point_x, point_y))

                slides = int(slides)
                length = Decimal(length)
                edge_sounds = [int(x) for x in edge_sounds.split("|")]

                edge_sets = []
                for edge_set in edge_sets_str.split("|"):
                    normal_set, addition_set = edge_set.split(":")

                    normal_set = int(normal_set)
                    addition_set = int(addition_set)

                    edge_sets.append((TimingPointSampleSet(normal_set), TimingPointSampleSet(addition_set)))

                if len(hit_sample) > 0:
                    hit_sample = create_hit_sample(hit_sample[-1])
                else:
                    hit_sample = HitSample()

                if curve_type == CurveType.BEZIER:
                    curves = []
                    curr_curve = [(x, y)]

                    prev_point = (-1, -1)  # sentinel
                    for point in curve_points:
                        if point[0] == prev_point[0] and point[1] == prev_point[1]:
                            curves.append(Curve(CurveType.BEZIER, curr_curve))
                            curr_curve = [point]
                        else:
                            curr_curve.append(point)

                        prev_point = point

                    curves.append(Curve(CurveType.BEZIER, curr_curve))
                else:
                    curves = [
                        Curve(curve_type, [(x, y), *curve_points])
                    ]

                beatmap.hit_objects.append(Slider(
                    x, y, start_time, object_type, create_hit_sound(hit_sound), new_combo, combo_to_skip,
                    hit_sample, curves, slides, length, edge_sounds, edge_sets))
            elif object_type == HitObjectType.SPINNER:
                end_time, *hit_sample = object_params

                end_time = int(end_time)

                if len(hit_sample) > 0:
                    hit_sample = create_hit_sample(hit_sample[-1])
                else:
                    hit_sample = HitSample()

                beatmap.hit_objects.append(Spinner(
                    x, y, start_time, object_type, create_hit_sound(hit_sound), new_combo, combo_to_skip, hit_sample,
                    end_time))
            elif object_type_flag == HitObjectType.HOLD_NOTE.value:
                pass

    populate_timing_point_properties(beatmap)
    populate_slider_properties(beatmap)

    return beatmap


if __name__ == "__main__":
    beatmap = load("sample_beatmap/diff1.osu")
    