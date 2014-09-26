OpenOPC
=======

This is a clone of http://openopc.sourceforge.net, with modifications to make it use distutils



About OpenOPC
-------------------
OpenOPC for Python is a free, open source OPC (OLE for Process Control) toolkit designed for use with the popular Python programming language. The unique features that set it apart from the many commercially available OPC toolkits include...

Easy to use
------------------
Because the OpenOPC library implements a minimal number of Python functions which may be chained together in a variety of ways, the library is simple to learn and easy to remember. In its simplest form, you can read and write OPC items as easily as any variable in your Python program...
print opc['Square Waves.Int4']
opc['Square Waves.Real8'] = 100.0
Cross platform support

OpenOPC works with both Windows and non-Windows platforms. It has been tested with Windows, Linux, and Mac OS X.
Functional programming style

OpenOPC allows OPC calls to be chained together in an elegant, functional programming style. For example, you can read the values of all items matching a wildcard pattern using a single line of Python code!
opc.read(opc.list('Square Waves.*'))
Designed for dynamic languages

Most OPC toolkits today are designed for use with static system languages (such as C++ or C#), providing a close mapping to the underlying Win32 COM methods. OpenOPC discards this cumbersome model and instead attempts to take advantage of the dynamic language features provided by Python.

OpenOPC is also one of the very few OPC-DA toolkits available for any dynamic language, and future support is planned for Ruby.
EXAMPLE: Minimal working program

    import OpenOPC
    opc = OpenOPC.client()
    opc.connect('Matrikon.OPC.Simulation')
    print opc['Square Waves.Real8']
    opc.close()

This project utilizes the de facto OPC-DA (Win32 COM-based) industrial automation standard. If you are looking for an OPC XML-DA library for Python, then please visit the PyOPC project.


OpenOPC Gateway Service
---------------------------------
The Gateway Service is an optional Windows service which handles all the Win32 COM/DCOM calls used by the OpenOPC library module. This offers the following potential advantages:

Avoidance of DCOM security headaches and firewall issues when running the OPC client and OPC server on different nodes.
The ability to write OPC client applications that can run on non-Windows platforms such as Linux, Unix, and Mac OS X.
Installing the service

    C:\OpenOPC\bin> OpenOPCService.exe -install
    Installing service OpenOpcService
    Service installed
    Starting the service

    C:\OpenOPC\bin> net start zzzOpenOpcService
    Stopping the service

    C:\OpenOPC\bin> net stop zzzOpenOpcService


**NOTE**: If you want to use the OpenOPC Gateway service from another machine as a client and are using OpenOPC 1.2 then you must
set the environment variable in windows and restart the gateway service:

    OPC_GATE_HOST=x.x.x.x

Reference:
http://sourceforge.net/p/openopc/discussion/709251/thread/b0216f58/


OpenOPC Library Tutorial
-------------------------------

The best way to learn the OpenOPC library is by trying it interactively from the Python Shell. The following examples use the Matrikon OPC Simulation Server which you can download for free from the company's website. We recommended you use a simulation server such as this one while learning OpenOPC as opposed to testing using a "live" OPC server.

#### 1. Import the OpenOPC module

Start by making the OpenOPC library available to your application. This imports the OpenOPC.py module file located in the lib/site-packages/ directory.

    >>> import OpenOPC
    
#### 2. Create OpenOPC instance (DCOM mode)

DCOM mode is used to talk directly to OPC servers without the need for the OpenOPC Gateway Service. This mode is only available to Windows clients.

    >>> opc = OpenOPC.client()
    
#### 2. Create OpenOPC instance (Open mode)

In Open mode a connection is made to the OpenOPC Gateway Service running on the specified node. This mode is available to both Windows and non-Windows clients.

    
    >>> opc = OpenOPC.open_client('localhost')

#### 3. Getting a list of available OPC servers

    
    >>> opc.servers()
    ['Matrikon.OPC.Simulation.1', 'Kepware.KEPServerEX.V4']

    
#### 4. Connect to OPC Server

Connect to the specified OPC server. The function returns True if the connection was successful, False on failure.
    
    >>> opc.connect('Matrikon.OPC.Simulation')
    True
    
If the OPC server is running on a different node, you can include the optional host parameter...

    >>> opc.connect('Matrikon.OPC.Simulation', 'localhost')
    True

#### 5. Reading a single item

Read the specified OPC item. The function returns a (value, quality, timestamp) tuple. If the call fails, the quality will be set to 'Error'.

    >>> opc.read('Random.Int4')
    (19169, 'Good', '06/24/07 15:56:11')
    >>> value, quality, time = opc.read('Random.Int4')
    
When using the special short form of the function, only the value portion is returned. If any problems are encountered, value will be set to None.

    >>> value = opc['Random.Int4']
    
#### 6. Reading multiple items

Multiple values may be read with a single call by passing a list of item names. Whenever a list is provided as input, the read function returns back a list of (name, value, quality, time) tuples.

    >>> opc.read( ['Random.Int2', 'Random.Real4', 'Random.String'] )
    [('Random.Int2', 28145, 'Good', '06/24/07 17:44:43'), ('Random.Real4', 19025.2324, 'Good', '06/24/07 17:44:43'), ('Random.String', 'your', 'Good', '06/24/07 17:44:43')]


There is a special version of read function called iread (Iterative Read). iread returns a Python generator which can be used to iterate through the returned results, item by item.

    for name, value, quality, time in opc.iread( ['Random.Int2', 'Random.Int4'] ):
       print name, value


#### 7. Reading items using OPC Groups

For best performance it is often necessary to place the items into a named group, then repeatedly request the group's values be updated. Including both the item list along with a group name will cause a new group to be defined and an initial read to be preformed.

    >>> tags = ['Random.String', 'Random.Int4', 'Random.Real4']
    >>> opc.read(tags, group='test')
    [('Random.String', 'options', 'Good', '06/24/07 23:38:24'), ('Random.Int4', 31101, 'Good', '06/24/07 23:38:24'), ('Random.Real4', 19933.958984375, 'Good', '06/24/07 23:38:24')]
    
Once the group has been defined, you can re-read the items in the group by supplying only the group name. You can repeat this call as often as necessary.

    >>> opc.read(group='test')
    [('Random.String', 'clients', 'Good', '06/24/07 23:38:30'), ('Random.Int4', 26308, 'Good', '06/24/07 23:38:30'), ('Random.Real4', 13846.63671875, 'Good', '06/24/07 23:38:30')]
    
When you are done using the group, be sure to remove it. This will free up any allocated resources. If the removal was successful True will be returned, otherwise False.

    >>> opc.remove('test')
    True
    
    
#### 8. Writing a single item

Writing a single item can be accomplished by submitting a (name, value) tuple to the write function. If the write was successful True is returned, or False on failure.

    >>> opc.write( ('Triangle Waves.Real8', 100.0) )
    'Success'
    You can also use the short form...
    >>> opc['Triangle Waves.Real8'] = 100.0
    
    
#### 9. Writing multiple items

To write multiple items at once, submit a list of (name, value) tuples. The function returns a list of (name, status) tuples letting you know for each item name if the write attempt was successful or not.

    >>> opc.write( [('Triangle Waves.Real4', 10.0), ('Random.String', 20.0)] )
    [('Triangle Waves.Real4', 'Success'), ('Random.String', 'Error')]
    
The iwrite function returns a generator designed for iterating through the return statuses item by item...

    for item, status in opc.iwrite( [('Triangle Waves.Real4', 10.0), ('Random.String', 20.0)] ):
       print item, status
       
#### 10. Getting error message strings

Including the optional include_error=True parameter will cause many of the OpenOPC functions to append a descriptive error message to the end of each item tuple. In the case of the write function, it will return (name, status, error) tuples.

    >>> opc.write( [('Triangle Waves.Real4', 10.0), ('Random.Int4', 20.0)], include_error=True)
    [('Triangle Waves.Real4', 'Success', 'The operation completed successfully'), ('Random.Int4', 'Error', "The item's access rights do not allow the operation")]

#### 11. Retrieving item properties

Requesting properties for a single item returns a list of (id, description, value) tuples. Each tuple in the list represents a single property.
    >>> opc.properties('Random.Int4')
    [(1, 'Item Canonical DataType', 'VT_I4'), (2, 'Item Value', 491), (3, 'Item Quality', 'Good'), (4, 'Item Timestamp', '06/25/07 02:24:44'), (5, 'Item Access Rights', 'Read'), (6, 'Server Scan Rate', 100.0), (7, 'Item EU Type', 0), (8, 'Item EUInfo', None), (101, 'Item Description', 'Random value.')]
    
If a list of items is submitted, the item name will be appended to the beginning of each tuple to produce a list of (name, id, description, value) tuples.

    >>> opc.properties( ['Random.Int2', 'Random.Int4', 'Random.String'] )
    [('Random.Int2', 1, 'Item Canonical DataType', 'VT_I2'), ('Random.Int2', 2, 'Item Value', 4827), ('Random.Int2', 3, 'Item Quality', 'Good'), ('Random.Int2', 4, 'Item Timestamp', '06/25/07 02:35:28'), ('Random.Int2', 5, 'Item Access Rights', 'Read'), ('Random.Int2', 6, 'Server Scan Rate', 100.0), ('Random.Int2', 7, 'Item EU Type', 0), ('Random.Int2', 8, 'Item EUInfo', None), ('Random.Int2', 101, 'Item Description', 'Random value.'), ('Random.Int4', 1, 'Item Canonical DataType', 'VT_I4'), ('Random.Int4', 2, 'Item Value', 14604), ('Random.Int4', 3, 'Item Quality', 'Good'), ('Random.Int4', 4, 'Item Timestamp', '06/25/07 02:35:28'), ('Random.Int4', 5, 'Item Access Rights', 'Read'), ('Random.Int4', 6, 'Server Scan Rate', 100.0), ('Random.Int4', 7, 'Item EU Type', 0), ('Random.Int4', 8, 'Item EUInfo', None), ('Random.Int4', 101, 'Item Description', 'Random value.'), ('Random.String', 1, 'Item Canonical DataType', 'VT_BSTR'), ('Random.String', 2, 'Item Value', 'profit...'), ('Random.String', 3, 'Item Quality', 'Good'), ('Random.String', 4, 'Item Timestamp', '06/25/07 02:35:28'), ('Random.String', 5, 'Item Access Rights', 'Read'), ('Random.String', 6, 'Server Scan Rate', 100.0), ('Random.String', 7, 'Item EU Type', 0), ('Random.String', 8, 'Item EUInfo', None), ('Random.String', 101, 'Item Description', 'Random value.')]
    
The optional id parameter can be used to limit the returned value to that of a single property...

    >>> opc.properties('Random.Int4', id=1)
    'VT_I4'

Like other OpenOPC function calls, providing a list of items causes the item names to be included in the output...
    
    >>> opc.properties( ['Random.Int2', 'Random.Int4', 'Random.String'], id=1)
    [('Random.Int2', 'VT_I2'), ('Random.Int4', 'VT_I4'), ('Random.String', 'VT_BSTR')]

The id parameter can also be used to specify a list of ids...

    >>> opc.properties('Random.Int4', id=(1,2,5))
    [(1, 'VT_I4'), (2, 1869), (5, 'Read')]


#### 12. Getting a list of available items

List nodes at the root of the tree...

    >>> opc.list()
    ['Simulation Items', 'Configured Aliases']

List nodes under the Simulation Items branch...

    >>> opc.list('Simulation Items')
    ['Bucket Brigade', 'Random', 'Read Error', 'Saw-toothed Waves', 'Square Waves', 'Triangle Waves', 'Write Error', 'Write Only']

Use the "." character as a seperator between branch names...

    >>> opc.list('Simulation Items.Random')
    ['Random.ArrayOfReal8', 'Random.ArrayOfString', 'Random.Boolean', 'Random.Int1', 'Random.Int2', 'Random.Int4', 'Random.Money', 'Random.Qualities', 'Random.Real4', 'Random.Real8', 'Random.String', 'Random.Time', 'Random.UInt1', 'Random.UInt2', 'Random.UInt4']

You can use Unix and DOS style wildcards...
    
    >>> opc.list('Simulation Items.Random.*Real*')
    ['Random.ArrayOfReal8', 'Random.Real4', 'Random.Real8']

If recursive=True is included, you can include wildcards in multiple parts of the path. The function will go thru the entire tree returning all children (leaf nodes) which match.

    >>> opc.list('Sim*.R*.Real*', recursive=True)
    ['Random.Real4', 'Random.Real8', 'Read Error.Real4', 'Read Error.Real8']

Including the optional flat=True parameter flattens out the entire tree into leaf nodes, freeing you from needing to be concerned with the hierarchical structure. (Note that this function is not implemented consistantly in many OPC servers)

    >>> opc.list('*.Real4', flat=True)
    ['Bucket Brigade.Real4', 'Random.Real4', 'Read Error.Real4', 'Saw-toothed Waves.Real4', 'Square Waves.Real4', 'Triangle Waves.Real4', 'Write Error.Real4', 'Write Only.Real4']

You can also submit a list of item search patterns. The returned results will be a union of the matching nodes.

    >>> opc.list(('Simulation Items.Random.*Int*', 'Simulation Items.Random.Real*'))
    ['Random.Int1', 'Random.Int2', 'Random.Int4', 'Random.UInt1', 'Random.UInt2', 'Random.UInt4', 'Random.Real4', 'Random.Real8']


#### 13. Retrieving OPC server information

    >>> opc.info()
    [('Host', 'localhost'), ('Server', 'Matrikon.OPC.Simulation'), ('State', 'Running'), ('Version', '1.1 (Build 307)'), ('Browser', 'Hierarchical'), ('Start Time', '06/24/07 13:50:54'), ('Current Time', '06/24/07 18:30:11'), ('Vendor', 'Matrikon Consulting Inc (780) 448-1010 http://www.matrikon.com')]


#### 14. Combine functions together

The output from many of the OpenOPC functions can be used as input to other OpenOPC functions. This allows you to employ a functional programming style which is concise and doesn't require the use of temporary variables.

Read the values of all Random integer items...

    >>> opc.read(opc.list('Simulation Items.Random.*Int*'))
    [('Random.Int1', 99, 'Good', '06/24/07 22:44:28'), ('Random.Int2', 26299, 'Good', '06/24/07 22:44:28'), ('Random.Int4', 17035, 'Good', '06/24/07 22:44:28'), ('Random.UInt1', 77, 'Good', '06/24/07 22:44:28'), ('Random.UInt2', 28703, 'Good', '06/24/07 22:44:28'), ('Random.UInt4', 23811.0, 'Good', '06/24/07 22:44:28')]

Read property #1 (data type) of all Real4 items...

    >>> opc.properties(opc.list('*.Real4', flat=True), id=1)
    [('Bucket Brigade.Real4', 'VT_R4'), ('Random.Real4', 'VT_R4'), ('Read Error.Real4', 'VT_R4'), ('Saw-toothed Waves.Real4', 'VT_R4'), ('Square Waves.Real4', 'VT_R4'), ('Triangle Waves.Real4', 'VT_R4'), ('Write Error.Real4', 'VT_R4'), ('Write Only.Real4', 'VT_R4')]

Read the value of all Triangle Wave integers and then write the values back out to the OPC server. (A better example would be to do this between two different OPC servers!)
    
    >>> opc.write(opc.read(opc.list('Simulation Items.Triangle Waves.*Int*')))
    [('Triangle Waves.Int1', 'Success'), ('Triangle Waves.Int2', 'Success'), ('Triangle Waves.Int4', 'Success'), ('Triangle Waves.UInt1', 'Success'), ('Triangle Waves.UInt2', 'Success'), ('Triangle Waves.UInt4', 'Success')]

The short form of the read and write functions are useful for building easy to read calculations...

    >>> opc['Square Waves.Real4'] = ( opc['Random.Int4'] * opc['Random.Real4'] ) / 100.0

Remove all named groups which were created with the read function...

    >>> opc.remove(opc.groups())
    
    
#### 15. Disconnecting from the OPC server

    >>> opc.close()
    
    
    
    
OpenOPC Command-line Client
-----------------------------------------------------

To the best of our knowledge, the OpenOPC project includes the only publically available command-line based OPC client. Unlike graphical OPC clients, this client can be easily used in scripts or batch files. And because of its piping capability (i.e. chaining commands together), it is far more powerful than other OPC clients.

#### Read items

    C:\> opc -r Random.String Random.Int4 Random.Real8
    Random.String  Your       Good  06/25/07 23:46:33
    Random.Int4    19169      Good  06/25/07 23:46:33
    Random.Real8   8009.5730  Good  06/25/07 23:46:33
    
    Read 3 of 3 items (0.02 seconds)


#### Multiple output styles

    C:\> opc -r Random.String Random.Int4 Random.Real8 -o csv
    Random.String,--,Good,06/25/07 23:58:16
    Random.Int4,15724,Good,06/25/07 23:58:16
    Random.Real8,5846.7234,Good,06/25/07 23:58:16


#### List available items

    C:\> opc -f Random.*Int*
    Random.Int1
    Random.Int2
    Random.Int4
    Random.UInt1
    Random.UInt2
    Random.UInt4
    
    
#### Combine commands using pipes

    C:\> opc -f Random.*Int* | opc -r -
    Random.Int1   0           Good  06/25/07 23:52:16
    Random.Int2   18467       Good  06/25/07 23:52:16
    Random.Int4   6334        Good  06/25/07 23:52:16
    Random.UInt1  206         Good  06/25/07 23:52:16
    Random.UInt2  19169       Good  06/25/07 23:52:16
    Random.UInt4  15724.0000  Good  06/25/07 23:52:16
    
    Read 6 of 6 items (0.02 seconds)


#### Read a collection of items and values into a CSV file, edit the item values using a spreadsheet or other software, then write the new values back to the OPC server...

    C:\> opc -f "Triangle Waves.*Int*" | opc -r - -o csv >data.csv
    
    C:\> opc -w - < data.csv
    Triangle Waves.Int1   Success
    Triangle Waves.Int2   Success
    Triangle Waves.Int4   Success
    Triangle Waves.UInt1  Success
    Triangle Waves.UInt2  Success
    Triangle Waves.UInt4  Success
    
    Wrote 6 of 6 items (0.02 seconds)
    
    
#### Data logger

Read values of items every 60 seconds, continually logging the results to a file until stopped by Ctrl-C...

    C:\> opc Random.Int4 Random.Real8 -L 60 >data.log 
    
    
#### Command usage summary

    C:\> opc 
    OpenOPC Command Line Client 1.1.6
    Copyright (c) 2007-2008 Barry Barnreiter (barry_b@users.sourceforge.net)
    
    Usage:  opc [OPTIONS] [ACTION] [ITEM|PATH...]
    
    Actions:
      -r, --read                 Read ITEM values (default action)
      -w, --write                Write values to ITEMs (use ITEM=VALUE)
      -p, --properties           View properties of ITEMs
      -l, --list                 List items at specified PATHs (tree browser)
      -f, --flat                 List all ITEM names (flat browser)
      -i, --info                 Display OPC server information
      -q, --servers              Query list of available OPC servers
      -S, --sessions             List sessions in OpenOPC Gateway Service
    
    Options:
      -m MODE, --mode=MODE       Protocol MODE (dcom, open) (default: OPC_MODE)
      -C CLASS,--class=CLASS     OPC Automation CLASS (default: OPC_CLASS)
      -n NAME, --name=NAME       Set OPC Client NAME (default: OPC_CLIENT)
      -h HOST, --host=HOST       DCOM OPC HOST (default: OPC_HOST)
      -s SERV, --server=SERVER   DCOM OPC SERVER (default: OPC_SERVER)
      -H HOST, --gate-host=HOST  OpenOPC Gateway HOST (default: OPC_GATE_HOST)
      -P PORT, --gate-port=PORT  OpenOPC Gateway PORT (default: OPC_GATE_PORT)
    
      -F FUNC, --function=FUNC   Read FUNCTION to use (sync, async)
      -c SRC,  --source=SOURCE   Set data SOURCE for reads (cache, device, hybrid)
      -g SIZE, --size=SIZE       Group tags into SIZE items per transaction
      -z MSEC, --pause=MSEC      Sleep MSEC milliseconds between transactions
      -u MSEC, --update=MSEC     Set update rate for group to MSEC milliseconds
      -t MSEC, --timeout=MSEC    Set read timeout to MSEC mulliseconds
    
      -o FMT,  --output=FORMAT   Output FORMAT (table, values, pairs, csv, html)
      -L SEC,  --repeat=SEC      Loop ACTION every SEC seconds until stopped
      -y ID,   --id=ID,...       Retrieve only specific Property IDs
      -a STR,  --append=STR,...  Append STRINGS to each input item name
      -x N     --rotate=N        Rotate output orientation in groups of N values
      -v,      --verbose         Verbose mode showing all OPC function calls
      -e,      --errors          Include descriptive error message strings
      -R,      --recursive       List items recursively when browsing tree
      -,       --pipe            Pipe item/value list from standard input
    
