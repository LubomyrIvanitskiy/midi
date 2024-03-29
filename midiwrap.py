import pretty_midi
from pretty_midi import utilities
import pandas as pd
import libfmp.c1
import instruments


def dataframe_to_midi(df_notes, output_file=None):
    """
    Pandas DataFrame in format columns=['Start', 'Duration', 'Pitch', 'Velocity', 'Name', 'Program']
    :param output_file:
    :param df_notes:
    :return:
    """
    melody = pretty_midi.PrettyMIDI()

    track_names = pd.unique(df_notes.Name)
    for track_name in track_names:
        track_records = df_notes[df_notes.Name == track_name]
        instrument = pretty_midi.Instrument(program=track_records.iloc[0].Program, name=track_name)
        for index, note_record in track_records.iterrows():
            start, duration, pitch, velocity, name, program = note_record.values
            note = pretty_midi.Note(velocity=velocity, pitch=pitch, start=start, end=start + duration)
            instrument.notes.append(note)
        melody.instruments.append(instrument)
    if output_file:
        melody.write(output_file)
    return melody


def csv_to_midi(csv):
    return dataframe_to_midi(pd.read_csv(csv))


def drum_to_pitch(drum_name: instruments.DrumType):
    return utilities.drum_name_to_note_number(drum_name)


class MelodyBuilder:

    def __init__(self):
        self.melody = pretty_midi.PrettyMIDI()
        self.instruments = {}

    def add_note(self, pitch, time, duration, instrument_name):
        """

        :param pitch: 0..127
        :param time: float in sec
        :param duration: float in sec
        :param instrument_name: import instruments for constants
        :return:
        """
        if instrument_name in self.instruments:
            instrument = self.instruments[instrument_name]
        else:
            if instrument_name == instruments.Drums:
                instrument = pretty_midi.Instrument(program=0, name=instrument_name, is_drum=True)
            else:
                instrument = pretty_midi.Instrument(program=utilities.instrument_name_to_program(instrument_name),
                                                    name=instrument_name, is_drum=False)
            self.instruments[instrument_name] = instrument
            self.melody.instruments.append(instrument)
        note = pretty_midi.Note(velocity=125, pitch=pitch, start=time, end=time + duration)
        instrument.notes.append(note)

    def write_to_file(self, output_file):
        self.melody.write(output_file)

    def show_piano_roll(self):
        result = []
        for instrument in self.instruments:
            notes = self.instruments[instrument].notes
            for note in notes:
                result.append((note.start, note.end - note.start, note.pitch, note.velocity / 128, instrument))
        libfmp.c1.visualize_piano_roll(result)


class MidiFile:

    def __init__(self, file):
        self._midi_data = pretty_midi.PrettyMIDI(file)
        midi_list = []

        for instrument in self._midi_data.instruments:
            for note in instrument.notes:
                start = note.start
                duration = note.end - start
                pitch = note.pitch
                velocity = note.velocity
                midi_list.append([start, duration, pitch, velocity, instrument.name, instrument.program])

        midi_list = sorted(midi_list, key=lambda x: (x[0], x[2]))

        self.notes = pd.DataFrame(midi_list, columns=['Start', 'Duration', 'Pitch', 'Velocity', 'Name', 'Program'])

    def remove_duplicates(self):
        self.notes

    def synthesize(self, fs=22050):
        audio_data = self._midi_data.synthesize(fs=fs)
        return audio_data, fs

    def piano_roll_data(self):
        records = self.notes[self.notes.columns[:-1]]

        result = []
        for index, record in records.iterrows():
            values = list(record.values)
            values[3] = values[3] / 128
            result.append(tuple(values))
        return result

    def show_piano_roll(self, figsize=(8, 3), velocity_alpha=True):
        libfmp.c1.visualize_piano_roll(self.piano_roll_data(), figsize=figsize, velocity_alpha=velocity_alpha)

    def to_csv(self, out_file):
        self.notes.to_csv(out_file, sep=';', quoting=2, float_format='%.3f', index=False)
        with open(out_file, 'r', encoding='utf-8') as file:
            csv_str = file.readlines()
        print(csv_str[0:4])

    def track_names(self):
        return pd.unique(self.notes.Name)


if __name__ == "__main__":
    midi = MidiFile('data/fur_elise.mid')
    track_names = midi.track_names()
    print("Tracks: ", track_names)
    for track_name in track_names:
        dataframe_to_midi(midi.notes[midi.notes.Name == track_name], f"data/out_fur_elise_{track_name.lower()}.mid")
    midi.to_csv("out_to_elise.csv")

    melody = MelodyBuilder()
    instrument = instruments.AcousticGrandPiano
    melody.add_note(pitch=72, time=0, duration=1, instrument_name=instrument)
    melody.add_note(pitch=75, time=1, duration=1, instrument_name=instrument)
    melody.add_note(pitch=76, time=2, duration=1, instrument_name=instrument)
    melody.add_note(pitch=78, time=3, duration=1, instrument_name=instrument)
    melody.add_note(pitch=drum_to_pitch(instruments.DrumType.SideStick), time=4, duration=1, instrument_name=instruments.Drums)
    melody.write_to_file('crasy.mid')
