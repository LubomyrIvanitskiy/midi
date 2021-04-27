import pretty_midi
import pandas as pd
import libfmp.c1


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

    def synthesize(self, fs=22050):
        audio_data = self._midi_data.synthesize(fs=fs)
        return audio_data, fs

    def piano_roll_data(self):
        records = self.notes[midi.notes.columns[:-1]].to_records(index=False)
        result = list(records)
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
