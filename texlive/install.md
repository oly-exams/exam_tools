# Install TeXLive 2015

We found some problems with Texlive 2013 which comes in Ubuntu 14.04 LTS. Here are some installation instructions to install the latest version.


On Ubuntu (other Unix distributions should also work):
```bash
wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
tar -xzf install-tl-unx.tar.gz
cd `tar -tzf install-tl-unx.tar.gz | sed -e 'N;s/^\(.*\).*\n\1.*$/\1\n\1/;D'`
sudo ./install-tl --profile=../texlive.profile
```

Alias for the binaries:
```bash
mkdir -p /opt
sudo ln -s /usr/local/texlive/2015/bin/* /opt/texbin
```

* Estimated size: 2GB
* Estimated install time: XX min
