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
