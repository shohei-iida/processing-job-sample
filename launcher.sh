# For installing handmade package to ProcessingJob container.
#
# Usage:
# 1. Set $SCRIPT_DIR and $SCRIPT_NAME in this shell script. (Check `# Variables` section.)
# 2. Set arguments for target python script.
# 3. Set this shell script for `run_script` parameter of `run_processor()` on `run_processing.py`.
# 4. Run `python run_processing.py`.

# Variables
SCRIPT_DIR="./"
SCRIPT_NAME="main_routine.py"

# Consts
INPUT_DIR="/opt/ml/processing/input"
PACKAGE_NAME="processing-job-sample"

# Main
echo "Start job."
echo "ls -lha ./"
ls -lha ./
echo "ls -lha /opt/ml/processing/input/"
ls -lha /opt/ml/processing/input/
echo "ls -lha /opt/ml/processing/input/input/"
ls -lha /opt/ml/processing/input/input/
echo "ls -lha /opt/ml/processing/input/package/"
ls -lha /opt/ml/processing/input/package/

echo "Trying: cp $INPUT_DIR/package/$PACKAGE_NAME.tar.gz ./$PACKAGE_NAME.tar.gz"
cp $INPUT_DIR/package/$PACKAGE_NAME.tar.gz ./$PACKAGE_NAME.tar.gz

echo "Trying: tar zxvf ${PACKAGE_NAME}.tar.gz"
tar zxvf ${PACKAGE_NAME}.tar.gz

cd $PACKAGE_NAME
echo "cur dir: `pwd`"
pip install -r requirements.txt

cd $SCRIPT_DIR

input_dir=""
out_dir=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --input-dir)
            if [[ ! -z "$2" ]]; then
                input_dir="--input-dir $2"
                shift 2
            else
                echo "Error: --input-dir requires a file name."
                exit 1
            fi
            ;;
        --out-dir)
            if [[ ! -z "$2" ]]; then
                out_dir="--out-dir $2"
                shift 2
            else
                echo "Error: --out-dir requires a file name."
                exit 1
            fi
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "python $SCRIPT_NAME $input_dir $out_dir"
python $SCRIPT_NAME $input_dir $out_dir

echo "Finish job."
