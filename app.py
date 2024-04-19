import os
import streamlit as st
import demucs.separate
import random
import shutil  # Make sure to import shutil


def delete_files_in_directory(directory_path):
    """
    Deletes all files and folders in the specified directory.
    
    Args:
    directory_path (str): Path to the directory from which files and folders will be deleted.
    """
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # This removes the file or link
                print(f"Deleted {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Use shutil to remove directories
                print(f"Deleted directory {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def generate_hex_number():
    """Generate an 8-digit hexadecimal number as a string."""
    return '{:08x}'.format(random.randint(0, 0xFFFFFFFF))


def separate_audio(audio_file, model='mdx_extra', device='cpu'):
    """
    Separates the audio file using the Demucs model and returns the output directory.
    """
    output_path = os.path.join('temp', os.path.splitext(os.path.basename(audio_file))[0])
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    demucs.separate.main(["--mp3", "-n", model, "--device", device, audio_file])
    st.success(f"Yeah! Finished separating {os.path.basename(audio_file)[8:]}")    
    return output_path


def list_files(directory):
    """
    List files in a specified directory, filtering only MP3 files.
    """
    files = os.listdir(directory)
    return [f for f in files if f.lower().endswith('.mp3')]


def main():
    st.title('Audio Separator | Full Mix To Stems')
    st.write('Separate audio tracks into drums, bass, vocals, and other instruments.')

    hex_nr = generate_hex_number()

    audio_file = st.file_uploader("Choose an audio file (.mp3 or .wav)", type=['mp3', 'wav'])
    if audio_file is not None:
        
        file_path = os.path.join('temp', hex_nr+audio_file.name)
        with open(file_path, "wb") as f:
            f.write(audio_file.getbuffer())

        print(file_path)

        st.write("Original audio file:")
        st.audio(file_path)

        st.write('Listen to the original audio file while you wait.')
        with st.spinner('Files are processing... please wait, it can take a minute.'):

            output_directory = separate_audio(file_path)
            files = list_files(output_directory)
            st.write("-----------------------------------")
            st.subheader(f"Final separated stems for {audio_file.name[:-4]}")

            for file in files:
                file_path = os.path.join(output_directory, file)
                st.write(file)  # Display the file name
                st.audio(file_path)

            # Show all MP3 files in the folder 'separated/mdx_extra/test' as playable audio files
            name_of_file = audio_file.name[:-4]  # assuming the file extension is .mp3 or .wav, hence slicing off last 4 chars
            specific_directory = f'separated/mdx_extra/{hex_nr+name_of_file}'  # Adjust the path as needed
            
            if os.path.exists(specific_directory):
                audio_files = list_files(specific_directory)
                if audio_files:
                    for audio_file in audio_files:
                        file_path = os.path.join(specific_directory, audio_file)
                        st.write(audio_file)  # Display the file name before the player
                        st.audio(file_path)
                else:
                    st.info("No MP3 files found in the directory.")
            else:
                st.error(f"The directory {specific_directory} does not exist.")

            #delete_files_in_directory('temp')
            #delete_files_in_directory('separated/mdx_extra')


if __name__ == "__main__":
    main()
