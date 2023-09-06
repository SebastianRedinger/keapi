.. KeAPI documentation master file, created by
   sphinx-quickstart on Wed Sep 28 15:55:39 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

KeAPI Documentation
===================

KeApi is an easy-to-use Python interface to commuicate with a KEBA PLC over
WebSockets. This API can only be used in combination with
**Robot Control WebAPI** installed on your PLC.

The goal of this API is to control a robot from a 3rd party application.

This interface provides functionality to:
 - Start and execute commands on the PLC
 - Set and receive variables on the PLC
 - Subscribe to cyclic and event based topics

Software Unit Requirements
""""""""""""""""""""""""""
| **RobotControl WebAPI 1.1.0**
| **RobotControl API 1.1.0**


.. toctree::
   :maxdepth: 2
   :caption: Introduction:

   installation
   getting_started
   api_reference
   class_reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
