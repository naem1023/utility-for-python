function copy_static_server() {
  echo copy staic server
  cd "$ROOT"/services/src/static-web-server || exit

  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    linux_platform=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
    echo "$linux_platform"

    if [[ "$linux_platform" == '"Ubuntu"' ]]; then
        ubuntu_version=$(lsb_release -d)
        echo "$ubuntu_version"

        if [[ "$ubuntu_version" == *"18.04"* ]];then
            echo "Os of system is same with os of docker."
        fi 
      fi
  fi
    
  rsync -Ra ./baikal --exclude config --exclude compiled "$OUT"/proto
}