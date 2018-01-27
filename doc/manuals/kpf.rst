KPF
===

KPF (KWIVER Packet Format) is used to persist object detections, tracks, events, and associated metadata in KWIVER. 
KPF uses a subset of YAML as its default text transport, as well as defining a set of semantic tokens useful for object detection and tracking, as well as activity recognition. 
It is hoped that by defining a core set of semantic concepts and their common representation, KPF will enable interoperability between various applications (e.g. trackers, detectors, GUIs, and evaluation tools.) 
KPF also provides for application-specific extensions to be persisted and parsed, yet ignored when not applicable.


From a design perspective, KPF tries to **provide** :

* unambiguous representation of objects, tracks, simple and complex events

  + both semantically ("timestamp is 4000 ... *4000 what?* ") 
  + and at the wire-level ("This box is 100, 200, 105, 205-- is that (x1,y1)-(x2,y2) or (x1,y1,w,h)?")

* relational support for linking, grouping, and mapping sets of items
* transport-agnostic representation (should be easily convertible between text, json, xml, protobuf)
* extensibility ("Hey, in Phase 2 the program just defined ten more event types!")
* explicit linkages between documents
* simplicity for common use cases, feasibility for most use cases
* convertibility from existing formats
* compatibility (in text mode) with command-line tools such as awk, grep, and perl

KPF tries to **avoid:** :

* MAGIC NUMBERS
* excessive redundancy and verbosity
* obsessive removal of all possible ambiguity

YAML
----

KPF uses `YAML <http://www.yaml.org>`_ as its default text transport. 
YAML was chosen over a more lighter-weight ad-hoc text format based on the following considerations:

*   YAML parsers are readily available for many languages
*   Although YAML is more verbose for very simple schemas, it provides more structure for complex concepts (such as activities)
*   Its flexibility reduces risk that future, possibly more complex concepts will require major revisions to the underlying format
*   It can still be represented as record-per-line text file, allowing rapid data analysis using standard tools such as awk, grep, and perl.

YAML can be rendered as a python object via
`http://yaml-online-parser.appspot.com/ <http://yaml-online-parser.appspot.com/>`_

Concepts
--------

As stated above, KPF is **not** a single file format or set of formats. There is no single "track file format" or "event file format".
Instead, KPF aims to provide a unified representation of the fundamental concepts common to computer vision applications, and a principled way to add new concepts. A KPF parser should be able to process any KPF-compliant input; the decision whether a particular instance meets the requirements of an application is an application-level decision, rather than an output of the parser.


In particular, if an application processes a KPF file containing both tokens it knows about (bounding boxes and frame numbers, for example) and tokens it does not recognize (say, activity instances) it should be able to process the recognized tokens
**without concern that the unknown tokens have altered the interpretation of the known tokens.**
In other words, the interpretation of a particular token is independent of the presence or absence of other tokens.

Packets and Domains
~~~~~~~~~~~~~~~~~~~

A recurring theme is that many concepts we want to represent (timestamps, object detections, event names) have natural representations which, if naively transcribed, become ambiguous due to different sources / references / coordinate systems. KPF handles this by sharing the representation between
**packets**
and
**domains.**

Packets
~~~~~~~

Packets are the semantic schema of a concept. Items such as timestamps, detections, events, bounding boxes are all represented by specific packets. Complex concepts (e.g. an activity instance) may be composed of multiple simpler packets (timestamps, track IDs, etc.)

Domains
~~~~~~~

A domain specifies the
**context of a packet**
. For example, a bounding box might have the domain of "pixel coordinates" or "world coordinates"; a timestamp might have the domain of "frame number" or "usecs since midnight 1 Jan 1970". A location might have the domain of "lat/lon", "utm", or "pixels". These are examples; default domains are provided for the common cases, but clients are free to specify a new custom domain. (The "social" aspects of
**defining**
a custom domain, ensuring that it does not conflict with somebody else's domain, whether or not it even needs to BE its own domain, are all explicitly outside the scope of KPF. By making the domain explicit, KPF allows for conflict detection, but does not handle conflict resolution.)


Roughly speaking, the packet tells you what something is; the domain grounds it in the units / coordinate frame / event vocabulary / etc.

Anatomy of a Packet
~~~~~~~~~~~~~~~~~~~

A packet's format is **[packet-tag][domain]:[space][payload]**

for example, the packet has the packet tag "g", domain "0", and payload "1080 229 1112 261" ::

  g0: 1080 229 1112 261

An equivalent XML representation might be ::

  <geometry domain="0">
    <payload> 1080 229 1112 261 </payload>
  </geometry>

Note that there is no subdivision of the payload into explicit corner points.

packet-tag
^^^^^^^^^^

The format of the payload is fixed by the tag. 
The packet tag is a string; as we add more concepts, we add more tags.

packet-domain
^^^^^^^^^^^^^


The interpretation of the payload is dictated by the domain.
The domain is an integer specifying the context in which to interpret the packet and effectively acts as a namespace. 
The general idea is that as more efforts define their own interpretations of tags (for example, different programs with different definitions for "U-turn"), 
each effort gets its own domain. For most packet types, a few pre-defined domains will suffice.
Inevitably, the problem of domain allocation and conflict resolution will arise. 
Similar to the Well Known Ports in /etc/services, we propose the following policy:

  * domains 0-9 are reserved and predefined as necessary.
  * Application-specific domains start numbering at 10
  
    +  the mapping of the domain to a specific application should be provided via the **meta** tag. 
    +  The meta tag has no domain, its payload is a string whose format is unspecified. 
    +  For example:

 ::
  
  { meta: "loc13 coordinate system: see /projects/foo/refcoords.txt"}

It may be that a different project was already using "loc13" without our knowledge.
Handling such organizational conflicts is explicitly outside the scope of KPF.

Packet Types
------------

Generally, when a number is undefined, "x" is used.

Strings should be quoted when they contain spaces and use \\ as an escape character.

Note the use of the elipsis '...' means multiple packets of the previous type may be provided.

The use of N signals a domain integer


+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| Packet     | YAML format                               | Definition                 | pre-defined domains / notes                                                                                    |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| id         | ::                                        | object identifier          | none; may start at 0 but should specify source via a meta packet.                                              |
|            |                                           |                            |                                                                                                                |
|            |    idN: int                               |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| ts         | ::                                        | timestamp                  | 0: frame number |br|                                                                                           |
|            |                                           |                            | 1: seconds since beginning of video  |br|                                                                      |
|            |    tsN: double                            |                            | 2: usecs since unix Epoch (1 Jan 1970 UTC)                                                                     |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| tsr        | ::                                        | timestamp range            | (same as ts) (maybe use 'x x' to mean "all the time"?)                                                         |
|            |                                           |                            |                                                                                                                |
|            |    tsrN: [ double double ]                |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| loc        | ::                                        | location                   | 0: pixel coordinates (z is undefined) |br|                                                                     |
|            |                                           |                            | 1: lon / lat / altitude-in-meters |br|                                                                         |
|            |    locN: x y z                            |                            | 2: UTM (e.g "17N 630084 4833438")                                                                              |
|            |                                           |                            |                                                                                                                |
|            |                                           |                            | Locations in world coordinates (e.g. via homographies) |br|                                                    |
|            |                                           |                            | should use a domain > 9 and specify the homography file used via a **meta** packet.                            |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| g          | ::                                        | bounding box               | 0: pixel coordinates                                                                                           |
|            |                                           |                            |                                                                                                                |
|            |    gN: x1 y1 x2 y2                        |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| poly       | ::                                        | polygon                    | 0: pixel coordinates                                                                                           |
|            |                                           |                            |                                                                                                                |
|            |   polyN: [ [x1,y1]                        |                            |                                                                                                                |
|            |            [x2,y2]                        |                            |                                                                                                                |
|            |              ...                          |                            |                                                                                                                |
|            |            [xM,yM] ]                      |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| conf       | ::                                        | confidence or likelihood   | none; may start at 0 but should specify source via a meta packet. |br|                                         |
|            |                                           |                            | Ground-truth should be represented via a 'src: truth' kv packet, rather than a confidence of 1.0.              |
|            |    confN: double                          |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| act        | ::                                        | activity                   | 0: VIRAT |br|                                                                                                  |
|            |                                           |                            | 1: vidtk |br|                                                                                                  |
|            |  actN: activity-name,                     |                            | 2: DIVA                                                                                                        |
|            |        id-packet,                         |                            |                                                                                                                |
|            |        timespan: [ { tsr } ... ],         |                            |                                                                                                                |
|            |        (*optional*) [kv] ...,             |                            |                                                                                                                |
|            |        actors: [ { id-packet }            |                            | Activity names are spelled out.  |br|                                                                          |
|            |                  timespan: [ { tsr } ... ]|                            | Participating objects should specify timestamp ranges in the same domains as the event itself. |br|            |
|            |                ] ...                      |                            | Timespans are represented as arrays of tsr packets to allow for future inclusion of synchronized world clocks. |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| eval       | ::                                        | evaluation result          | same protocol as id. The result-string is e.g. 'tp' for true positives, 'fa' for false alarms, etc.            |
|            |                                           |                            |                                                                                                                |
|            |    evalN: result-string                   |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| a          | ::                                        | attribute                  | same protocol as id. Specifies that the named attribute applies in the current scope.                          |
|            |                                           |                            |                                                                                                                |
|            |    aN: attribute_string                   |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| tag        | ::                                        | a packet / domain pair     | Used to link multiple files, i.e. 'tag: id0 collect5' in file A and 'tag: id3 collect5' in file B |br|         |
|            |                                           |                            | essentially means file A's id0 domain is the same as file B's id3 domain.                                      |
|            |    tag: packet string                     |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+
| kv         | ::                                        | key / value pair           | Keys are distinguished from KPF packets as they have no domain integer before the colon, i.e. '                |
|            |                                           |                            |                                                                                                                |
|            |    key: value                             |                            |                                                                                                                |
+------------+-------------------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------+


Use Cases
---------

Here we show an example of how a KPF file might evolve through a pipeline of detection, tracking, and scoring. 
The files are unrealistically short for brevity, but each line is meant to be complete.

Detection
~~~~~~~~~

A detector output might look like ::

  { meta: "cmdline0: run_detector param1 param2..." }
  { meta: "conf0: yolo person detector" }
  { meta: "id0 domain: yolo person detector" }**
  { id0: 0, ts0: 101, g0: 515 419 525 430, conf0: 0.8 }
  { id0: 1, ts0: 101, g0: 413 303 423 313, conf0: 0.3 }
  { id0: 2, ts0: 102, g0: 517 421 527 432, conf0: 0.7 }
  { id0: 3, ts0: 102, g0: 416 304 421 315, conf0: 0.2 }

Here the **id0** and **conf0** domains are specified to be the detections from yolo; 
the timestamp **ts0** and geometry **g0** domains are predefined to be frame number and pixel coordinates, respectively.

Tracking
~~~~~~~~

A tracker (detection linker) could take the above and generate the following. ::

  { meta: "cmdline0: run_detector param1 param2..." }
  { meta: "conf0: yolo person detector" }
  { meta: "id0 domain: yolo person detector" }
  { meta: "cmdline1: run_linker param1 param2..." }
  { meta: "id1 domain: track linker hash 0x85913" }
  { id0: 0, ts0: 101, g0: 515 419 525 430, conf0: 0.8, id1: 100 }
  { id0: 1, ts0: 101, g0: 413 303 423 313, conf0: 0.3, id1: 102 }
  { id0: 2, ts0: 102, g0: 517 421 527 432, conf0: 0.7, id1: 100 }
  { id0: 3, ts0: 102, g0: 416 304 421 315, conf0: 0.2, id1: 102 }


Here all the tracker has done is defined an additional domain for IDs (id1) which it uses to link detections into tracks.


Scoring
~~~~~~~
An evaluation run could take the output from the tracker and produce the following. ::

  { meta: "cmdline0: run_detector param1 param2..." }
  { meta: "conf0: yolo person detector" }
  { meta: "id0 domain: yolo person detector" }
  { meta: "cmdline1: run_linker param1 param2..." }
  { meta: "id1 domain: track linker hash 0x85913" }
  { meta: "cmdline2: score_tracks param1 param2..." }
  { meta: "overall track pd/fa count: 0.5 / 1" }
  { meta: "eval0 domain against id0" }
  { meta: "eval1 domain against id1" }
  { meta: "id2 domain false negatives from official_ground_truth.kpf" }
  { id0: 0, ts0: 101, g0: 515 419 525 430, conf0: 0.8, id1: 100, eval0: tp, eval1: tp }
  { id0: 1, ts0: 101, g0: 413 303 423 313, conf0: 0.3, id1: 102, eval0: fa, eval1: fa }
  { id0: 2, ts0: 102, g0: 517 421 527 432, conf0: 0.7, id1: 100, eval0: fa, eval1: tp }
  { id0: 3, ts0: 102, g0: 416 304 421 315, conf0: 0.2, id1: 102, eval0: fa, eval1: tp }
  { id2: 0, ts0: 101, g0: 600 550 605 610, eval0: fn, eval1: fn }
  { id2: 1, ts0: 102, g0: 603 553 608 615, eval0: fn, eval1: fn }

Here, the scoring code has done several things:

*   It has added a summary of its scoring results to the preamble via the **meta** packets.
*   It has added two sets of eval packets to each detection

    +   **eval0** is the detection-level result against **id0** 
    +   **eval1** is the track-level result against **id1.**
    
*   It has added a wholly new set of boxes in a new domain ( **id2** )
*   These are the false negatives (undetected boxes) from the ground-truth file named in the **meta** packet.

    +   These new tracks have IDs which collide with those from domain 0
    +   They are still separated since they come from a different domain.

This KPF file could be used for visualizing results.
One could easily imagine a pull-down menu allowing selection of individual ID domains populated with the text from the corresponding **meta** packet.

Diva Specific Schemas
---------------------

+------------+--------------------------------------------+---------------------------+
| File       | Description                                | Size                      |
+------------+--------------------------------------------+---------------------------+
| Geometry   | Frame level data for detections and tracks | n Detections * m Frames   |
+------------+--------------------------------------------+---------------------------+
| Label      | Detection and Track Identification         | n Objects                 |
+------------+--------------------------------------------+---------------------------+
| Activity   | Activity                                   | n Activities              |
+------------+--------------------------------------------+---------------------------+
| Region     | TBD                                        | TBD                       |
+------------+--------------------------------------------+---------------------------+

Geometry 
~~~~~~~~~

Schema Specification, (Line breaks are for clarity) ::

 { id0: detection-id, id1: track-id, ts0: frame-id, g0: geom-str, src: source
    [occlusion: (medium | heavy )]
    [confN: confidence...]
    [evalN: eval-tag...]
    [polyN: poly-str kv: keyframe [0|1] ] 
  }

Required Tags : id0, id1, tsN, g

**kv** Tags : src, occlusion

Example (simple) ::

  { id1: 0, id0: 37, ts0: 37, g0: 432 387 515 444, src: truth, occlusion: heavy }

Detection 37 is associated with track 0 on frame 37, and is a box from image coordinates (432, 387) to (515,444). 
This detection is ground truth and an annotator has marked the object's occlusion level as "heavy".


Example (slightly more complicated) ::

  { id1: 0, id0: 37, ts0: 37, ts1: 18.5, g0: 432 387 515 444 , src: truth, occlusion: heavy, eval0: fn, eval1: tp }

Same as previous example, but now with another timestamp (18.5 seconds since the beginning of the video) 
and results from an evaluation run: **eval0** marked it as a miss (false negative) in the detection domain,
while **eval1** found that it was a hit (true positive) in the track domain.

Label
~~~~~

Schema Specification ::

  { id1: track-id, obj_type: object_type } 

Required Tags : id1, obj_type

**kv** Tags : obj_type

Examples ::

  { id1: 35 , obj_type: Vehicle }
  { id1: 36 , obj_type: Vehicle }
  { id1: 5000 , obj_type: Parking_Meter }
  { id1: 5001 , obj_type: Dumpster }

Activity schema:
~~~~~~~~~~~~~~~~

Schema Specification, (Line breaks are for clarity) ::

  { actN: activity name, id_packet, src: source, 
          timespan: [ {tsr_packet} (...) ],
          actors: [ {id_packet, timespan: [ {tsr_packet} (...) ]}
                    (...) 
                  ]
  }

Note the (...) indicates multiple specifications of the previous *{ packets }* may be provided

Example (line breaks for clarity) ::

  { act2: Talking, id2: 3, src: truth, 
         timespan: [ { tsr0: [3293, 3314] } ],
         actors: [ { id1: 9,  timespan: [ {tsr0: [3293, 3314] } ] } ,
                   { id1: 12, timespan: [ {tsr0: [3293, 3314] } ] } , ]
  }

Here the activity is parsed as follows:

*   **act2:** this is an activity in domain 2 (notionally DIVA)
*   **Talking** is the activity name
*   **id2: 3** activity ID is 3 (explicitly also in domain 2, DIVA)
*   **src truth** the activity is a ground-truth activity 

    +  i.e. sourced from "truth"; other detectors would substitute their own sources

*   **timespan: [{tsr0: [3293, 3314]}]** The activity as a whole starts at frame 3293 and ends at 3314.
    Timestammps are domain 0 for frame range.
*   **actors:** Signals the start of the actor array

    *   **id1: 9** First actor is track ID 9
    *   **timespan: [{tsr0: [3293, 3314]}]** The first actor is participating in the activity from frames 3293 to 3314
    *   **id1: 12** Second actor is track ID 12
    *   **timespan: [{tsr0: [3293, 3314]}]** The second actor is also participating in the activity from frames 3293 to 3314

Timestamp ranges are stored as arrays in anticipation that multiple-camera activities.
They will be accessible from multiple time reference points (e.g. frames-since-video-start as well as world-clock-time.)

Regions
~~~~~~~

TBD

Questions and comments
~~~~~~~~~~~~~~~~~~~~~~

Please send any questions and/or comments to
`roddy.collins@kitware.com <mailto:roddy.collins@kitware.com>`_


.. |br| raw:: html

   <br />