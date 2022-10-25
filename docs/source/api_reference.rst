.. _apireference:

#############
API Reference
#############

First Class functions
=====================

.. currentmodule:: keapi
.. autosummary::
    connect_commands
    connect_subscriber
    get_variable
    create_variable_getter
    set_variable
    create_variable_setter

CommandServer
=============

.. currentmodule:: keapi
.. autosummary::
    CommandServer
    CommandServer.disconnect
    CommandServer.is_connected
    CommandServer.start
    CommandServer.exec

Ticket
======

.. currentmodule:: keapi
.. autosummary::
    Ticket
    Ticket.wait
    Ticket.requestid
    Ticket.state

SubscribeServer
===============

.. currentmodule:: keapi
.. autosummary::
    SubscribeServer
    SubscribeServer.disconnect
    SubscribeServer.is_connected
    SubscribeServer.subscribe
    SubscribeServer.unsubscribe

Compatibility Layer
===================
As some functions is not present in RcWebApi beta the compatibility layer
provides functionality to connect to the TcWebApi to achive those functions.
This is a temporary fix while RcWebApi is still in beta and will be removed in
the future.

.. currentmodule:: keapi.compat
.. autosummary::
    connect_tc_var
    TcVar.set_var
    TcVar.get_var
    connect_tc_prog
    TcProg.exec
    TcProg.start
    TcProg.stop
    TcProg.load_project
    TcProg.unload_project
    TcProg.is_prog_running