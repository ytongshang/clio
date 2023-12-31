# https://www.uvicorn.org/deployment/

# 判断是macos还是linux
cpu_num=1
if [ "$(uname)" == "Darwin" ]; then
    # get cpu core number
    cpu_num=$(sysctl -n hw.ncpu)
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # get cpu core number
    cpu_num=$(nproc)
fi

echo "cpu_num: ${cpu_num}"

uvicorn example.app:app \
--host "0.0.0.0" \
--port 8000 \
--workers "${cpu_num}" \
--loop uvloop \
--no-access-log \
--log-level info \
--timeout-keep-alive 5 \
--timeout-graceful-shutdown 30 \
--no-server-header \
--date-header \
--proxy-headers