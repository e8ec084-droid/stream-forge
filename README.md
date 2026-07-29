# stream-forge
 Distributed Python Event Processor

Python developers often use Java-based frameworks like Apache Flink or Spark to process massive streams of data, such as millions of IoT sensor
readings.,Creating a pure-Python distributed stream processor that addresses fault tolerance, state management, and exactly-once processing 
semantics is extremely challenging.,An example of this is seen in the case of an IoT fleet manager who needs to aggregate temperature data
from 50,000 trucks every 10 seconds.,In this scenario, StreamForge, a custom Python streaming engine based on Apache Kafka and Faust, 
is deployed with 20 parallel Python worker nodes.,The engine partitions the incoming data stream and the Python workers perform 'Windowed Aggregations' 
by calculating the 5-minute rolling average temperature per truck.,If a worker node, such as Worker Node #4, experiences a crash, StreamForge automatically redistributes
the partition to Worker #5 and retrieves its state from a RocksDB changelog.,This process ensures that no sensor reading is ever dropped or processed twice.
