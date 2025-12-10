Usage
=====

Python API
----------

To use Sanskrit Text in a project:

.. code-block:: python

    import sanskrit_text as skt

    text = "कवि भारतः"

    # Clean text
    clean_text = skt.clean(text)

    # Syllabification
    syllables = skt.get_syllables(text)

    # Varṇa decomposition and join
    viccheda = skt.split_varna(text, technical=True, flat=True)
    reconstructed = skt.join_varna(viccheda)

    # Ucchāraṇa information
    ucchaarana = skt.get_ucchaarana(text)
    signature = skt.get_signature(text)

Command Line Interface
----------------------

After installation, the :code:`skt` command is available:

.. code-block:: console

    $ skt clean "अ b १।"
    अ

    $ skt syllables "कवि भारतः"

    $ skt split-varna --technical --flat "कवि भारतः"

    $ skt ucchaarana "कवि"
    $ skt signature "कवि"
