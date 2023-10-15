import copy
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
    AudioFilename: str = ""
    """Location of the audio file relative to the current folder"""

    AudioLeadIn: int = 0
    """Milliseconds of silence before the audio starts playing"""

    AudioHash: str = ""
    """Deprecated"""

    PreviewTime: int = -1
    """Time in milliseconds when the audio preview should start"""

    Countdown: Countdown = Countdown.NORMAL
    """Speed of the countdown before the first hit object"""

    SampleSet: SampleSet = SampleSet.NORMAL
    """Sample set that will be used if timing points do not override it (Normal, Soft, Drum)"""

    StackLeniency: Decimal = Decimal("0.7")
    """Multiplier for the threshold in time where hit objects placed close together stack (0–1)"""

    Mode: GameMode = GameMode.STANDARD
    """Game mode"""

    LetterboxInBreaks: bool = False
    """Whether or not breaks have a letterboxing effect"""

    StoryFireInFront: bool = True
    """Deprecated"""

    UseSkinSprites: bool = False
    """Whether or not the storyboard can use the user's skin images"""

    AlwaysShowPlayfield: bool = False
    """Deprecated"""

    OverlayPosition: str = OverlayPosition.NO_CHANGE
    """Draw order of hit circle overlays compared to hit numbers"""

    SkinPreference: str = ""
    """Preferred skin to use during gameplay"""

    EpilepsyWarning: bool = False
    """Whether or not a warning about flashing colours should be shown at the beginning of the map"""

    CountdownOffset: int = 0
    """Time in beats that the countdown starts before the first hit object"""

    SpecialStyle: bool = False
    """Whether or not the "N+1" style key layout is used for osu!mania"""

    WidescreenStoryboard: bool = False
    """Whether or not the storyboard allows widescreen viewing"""

    SamplesMatchPlaybackRate: bool = False
    """Whether or not sound samples will change rate when playing with speed-changing mods"""


@dataclass
class Editor:
    DistanceSpacing: Decimal = Decimal(1)
    """Distance snap multiplier"""

    BeatDivisor: int = 4
    """Beat snap divisor"""

    GridSize: int = 64
    """Grid size"""

    TimelineZoom: Decimal = Decimal()
    """Scale factor for the object timeline"""

    Bookmarks: list[int] = default_field([])
    """Time in milliseconds of bookmarks"""


@dataclass
class Metadata:
    Title: str = ""
    """Romanised song title"""

    TitleUnicode: str = ""
    """Song title"""

    Artist: str = ""
    """Romanised song artist"""

    ArtistUnicode: str = ""
    """Song artist"""

    Creator: str = ""
    """Beatmap creator"""

    Version: str = ""
    """Difficulty name"""

    Source: str = ""
    """Original media the song was produced for"""

    Tags: list[str] = default_field([])
    """separated list of strings"""

    BeatmapID: int = -1
    """Difficulty ID"""

    BeatmapSetID: int = -1
    """Beatmap ID"""


@dataclass
class Difficulty:
    HPDrainRate: Decimal = Decimal(5)
    """HP setting (0–10)"""

    CircleSize: Decimal = Decimal(5)
    """CS setting (0–10)"""

    OverallDifficulty: Decimal = Decimal(5)
    """OD setting (0–10)"""

    ApproachRate: Decimal = Decimal(5)
    """AR setting (0–10)"""

    SliderMultiplier: Decimal = Decimal(5)
    """Base slider velocity in hundreds of osu! pixels per beat"""

    SliderTickRate: Decimal = Decimal(5)
    """Amount of slider ticks per beat"""


@dataclass
class Event:
    eventType: int | str
    """Type of the event. Some events may be referred to by either a name or a number."""

    startTime: int
    """Start time of the event, in milliseconds from the beginning of the beatmap's audio.
    For events that do not use a start time, the default is 0."""


@dataclass
class Background(Event):
    eventType = 0  # Background
    filename: str
    """Location of the background image relative to the beatmap directory.
    Double quotes are usually included surrounding the filename, but they are not required."""

    xOffset: int
    """Offset in osu! pixels from the centre of the screen."""

    yOffset: int
    """Offset in osu! pixels from the centre of the screen."""


@dataclass
class Video(Event):
    eventType = 1  # Video
    filename: str
    """Location of the background video relative to the beatmap directory.
    Double quotes are usually included surrounding the filename, but they are not required."""

    xOffset: int
    """Offset in osu! pixels from the centre of the screen."""

    yOffset: int
    """Offset in osu! pixels from the centre of the screen."""


@dataclass
class Break(Event):
    eventType = 2  # Break
    startTime: int
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
    KiaiTime: bool
    """Whether or not kiai time is enabled"""

    BarLine: bool
    """Whether or not the first barline is omitted in osu!taiko and osu!mania"""


@dataclass
class TimingPoint:
    time: Decimal  # should be int but some beatmaps have decimals
    """Start time of the timing section, in milliseconds from the beginning of the beatmap's audio. The end of the 
    timing section is the next timing point's time (or never, if this is the last timing point)."""

    meter: int
    """Amount of beats in a measure. Inherited timing points ignore this property."""

    sampleSet: int
    """Default sample set for hit objects."""

    sampleIndex: int
    """Custom sample index for hit objects. 0 indicates osu!'s default hitsounds."""

    volume: int
    """Volume percentage for hit objects."""

    uninherited: bool
    """Whether or not the timing point is uninherited."""

    effects: Effects
    """Bit flags that give the timing point extra effects. See the effects section."""


@dataclass
class InheritedTimingPoint(TimingPoint):
    svMultiplier: Decimal
    """A negative inverse slider velocity multiplier, as a percentage.
    For example, -50 would make all sliders in this timing section twice as fast as SliderMultiplier."""

    uninherited = False


@dataclass
class UninheritedTimingPoint(TimingPoint):
    beatDuration: Decimal
    """The duration of a beat, in milliseconds."""

    uninherited = True


@dataclass
class Colors:
    colors: list[tuple[int, ...]] = default_field([])
    """Combo Colors"""

    SliderTrackOverride: tuple[int, int, int] | None = None
    """Additive slider track colour"""

    SliderBorder: tuple[int, int, int] | None = None
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
    normalSet: TimingPointSampleSet = default_field(TimingPointSampleSet.DEFAULT)
    """Sample set of the normal sound."""

    additionSet: TimingPointSampleSet = default_field(TimingPointSampleSet.DEFAULT)
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

    hitSound: HitSound
    """Hitsound additions applied to the object"""

    newCombo: bool
    """Whether or not the object is the start of a new combo"""

    comboToSkip: int
    """How many combo colours to skip, a practice referred to as "colour hax".
    Only relevant if the object starts a new combo."""

    hitSample: HitSample
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
    curveType: CurveType
    """Type of curve"""

    curvePoints: list[tuple[int, int]]
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

    edgeSounds: list[int]
    """Hitsounds that play when hitting edges of the slider's curve. The first sound is the one that plays when the 
    slider is first clicked, and the last sound is the one that plays when the slider's end is hit."""

    edgeSets: list[tuple[TimingPointSampleSet, TimingPointSampleSet]]
    """Sample sets used for the edgeSounds. Each set is in the format normalSet:additionSet, with the same meaning as 
    in the hitsounds section."""

    endTime: int = 0  # to be populated after


@dataclass
class Spinner(HitObject):
    endTime: int


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

    timingPoints: list[TimingPoint] = default_field([])
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
                beatmap.general.AudioFilename = value
            elif key == "AudioLeadIn":
                beatmap.general.AudioLeadIn = int(value)
            elif key == "AudioHash":
                beatmap.general.AudioHash = value
            elif key == "PreviewTime":
                beatmap.general.PreviewTime = int(value)
            elif key == "Countdown":
                beatmap.general.Countdown = int(value)
            elif key == "SampleSet":
                beatmap.general.SampleSet = value
            elif key == "StackLeniency":
                beatmap.general.StackLeniency = Decimal(value)
            elif key == "Mode":
                beatmap.general.Mode = int(value)
            elif key == "LetterboxInBreaks":
                beatmap.general.LetterboxInBreaks = bool(int(value))
            elif key == "StoryFireInFront":
                beatmap.general.StoryFireInFront = bool(int(value))
            elif key == "UseSkinSprites":
                beatmap.general.UseSkinSprites = bool(int(value))
            elif key == "AlwaysShowPlayfield":
                beatmap.general.AlwaysShowPlayfield = bool(int(value))
            elif key == "OverlayPosition":
                beatmap.general.OverlayPosition = str(value)
            elif key == "SkinPreference":
                beatmap.general.SkinPreference = str(value)
            elif key == "EpilepsyWarning":
                beatmap.general.EpilepsyWarning = bool(int(value))
            elif key == "CountdownOffset":
                beatmap.general.CountdownOffset = int(value)
            elif key == "SpecialStyle":
                beatmap.general.SpecialStyle = bool(int(value))
            elif key == "WidescreenStoryboard":
                beatmap.general.WidescreenStoryboard = bool(int(value))
            elif key == "SamplesMatchPlaybackRate":
                beatmap.general.SamplesMatchPlaybackRate = bool(int(value))
        elif section == Section.EDITOR:
            key, value = line.split(":")

            if key == "DistanceSpacing":
                beatmap.editor.DistanceSpacing = Decimal(value)
            if key == "BeatDivisor":
                beatmap.editor.BeatDivisor = int(value)
            if key == "GridSize":
                beatmap.editor.GridSize = int(value)
            if key == "TimelineZoom":
                beatmap.editor.TimelineZoom = Decimal(value)
            if key == "Bookmarks":
                beatmap.editor.Bookmarks = [int(x) for x in value.split(",")]
        elif section == Section.METADATA:
            key, value = line.split(":", maxsplit=1)  # metadata might have more than one colon

            key = key.strip()
            value = value.strip()

            if key == "Title":
                beatmap.metadata.Title = value
            if key == "TitleUnicode":
                beatmap.metadata.TitleUnicode = value
            if key == "Artist":
                beatmap.metadata.Artist = value
            if key == "ArtistUnicode":
                beatmap.metadata.ArtistUnicode = value
            if key == "Creator":
                beatmap.metadata.Creator = value
            if key == "Version":
                beatmap.metadata.Version = value
            if key == "Source":
                beatmap.metadata.Source = value
            if key == "Tags":
                beatmap.metadata.Tags = value.split(" ")
            if key == "BeatmapID":
                beatmap.metadata.BeatmapID = int(value)
            if key == "BeatmapSetID":
                beatmap.metadata.BeatmapSetID = int(value)
        elif section == Section.DIFFICULTY:
            key, value = line.split(":")

            if key == "HPDrainRate":
                beatmap.difficulty.HPDrainRate = Decimal(value)
            if key == "CircleSize":
                beatmap.difficulty.CircleSize = Decimal(value)
            if key == "OverallDifficulty":
                beatmap.difficulty.OverallDifficulty = Decimal(value)
            if key == "ApproachRate":
                beatmap.difficulty.ApproachRate = Decimal(value)
            if key == "SliderMultiplier":
                beatmap.difficulty.SliderMultiplier = Decimal(value)
            if key == "SliderTickRate":
                beatmap.difficulty.SliderTickRate = Decimal(value)
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
                timing_point = UninheritedTimingPoint(
                    time, meter, sample_set, sample_index, volume, uninherited, effects, beat_length)
            else:
                timing_point = InheritedTimingPoint(
                    time, meter, sample_set, sample_index, volume, uninherited, effects, -100 / beat_length)

            beatmap.timingPoints.append(timing_point)
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
                beatmap.colors.SliderTrackOverride = color
            elif key == "SliderBorder":
                beatmap.colors.SliderBorder = color
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

                beatmap.hit_objects.append(Slider(
                    x, y, start_time, object_type, create_hit_sound(hit_sound), new_combo, combo_to_skip,
                    hit_sample, [
                        Curve(curve_type, curve_points)
                    ], slides, length, edge_sounds, edge_sets))
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

    return beatmap
