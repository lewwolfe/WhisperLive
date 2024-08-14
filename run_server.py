from pathlib import Path
import sys
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p',
                        type=int,
                        default=9090,
                        help="Websocket port to run the server on.")
    parser.add_argument('--backend', '-b',
                        type=str,
                        default='faster_whisper',
                        help='Backends from ["tensorrt", "faster_whisper"]')
    parser.add_argument('--faster_whisper_custom_model_path', '-fw',
                        type=str, default=None,
                        help="Custom Faster Whisper Model")
    parser.add_argument('--trt_model_path', '-trt',
                        type=str,
                        default=None,
                        help='Whisper TensorRT model path')
    parser.add_argument('--trt_multilingual', '-m',
                        action="store_true",
                        help='Boolean only for TensorRT model. True if multilingual.')
    parser.add_argument('--omp_num_threads', '-omp',
                        type=int,
                        default=1,
                        help="Number of threads to use for OpenMP")
    parser.add_argument('--no_single_model', '-nsm',
                        action='store_true',
                        help='Set this if every connection should instantiate its own model. Only relevant for custom model, passed using -trt or -fw.')
    args = parser.parse_args()

    # If running with faster_whisper backend and running as a stand-alone executable
    if args.backend == "faster_whisper" and getattr(sys, '_MEIPASS', False):
            # Import the original VAD (Voice Activity Detection) model class and module
            from faster_whisper.vad import SileroVADModel
            import faster_whisper.vad

            # Determine the directory where the script is running. If the script is run in a frozen environment
            # (e.g., a standalone executable created by PyInstaller), `_MEIPASS` will give the correct directory.
            # Otherwise, it will default to the script's directory.
            script_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))

            def _get_vad_model():
                """Returns the VAD model instance."""
                # Construct the path to the VAD model file within the 'assets' directory of the script.
                path = script_dir / "assets" / "silero_vad.onnx"
                # Return an instance of the SileroVADModel using the specified path.
                return SileroVADModel(path)

            # Monkey patch the `get_vad_model` function in the `faster_whisper.vad` module.
            # This replaces the original `get_vad_model` with our custom `_get_vad_model` function,
            # ensuring that the correct VAD model is loaded from the specified location.
            faster_whisper.vad.get_vad_model = _get_vad_model

    if args.backend == "tensorrt":
        if args.trt_model_path is None:
            raise ValueError("Please Provide a valid tensorrt model path")

    if "OMP_NUM_THREADS" not in os.environ:
        os.environ["OMP_NUM_THREADS"] = str(args.omp_num_threads)

    from whisper_live.server import TranscriptionServer
    server = TranscriptionServer()
    server.run(
        "0.0.0.0",
        port=args.port,
        backend=args.backend,
        faster_whisper_custom_model_path=args.faster_whisper_custom_model_path,
        whisper_tensorrt_path=args.trt_model_path,
        trt_multilingual=args.trt_multilingual,
        single_model=not args.no_single_model,
    )
