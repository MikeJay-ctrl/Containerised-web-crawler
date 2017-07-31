FROM ubuntu

RUN \
	apt-get update && \
	apt-get install -y python3 python3-pip && \
	rm -rf /var/lib/apt/lists/*


COPY utils/* test/* src/* ./

RUN pip3 install -r requirements.txt 

ENTRYPOINT ["/usr/bin/python3"]