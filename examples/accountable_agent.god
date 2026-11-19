# The accountable agent.
#
# The first flagship demo: an agent given exactly one folder, and
# nothing else. It declares the one power it may use, reads every file
# in the entrusted folder, fingerprints each one, and reports the
# count. It cannot read, write, or reach anything outside that folder:
# the host grant and the scroll's own permission narrow each other,
# and either one refusing stops the run.
#
# Read what it may touch first (runs nothing):
#   godcode permissions examples/accountable_agent.god
#
# Run it from the repo root, sandboxed, with the host granting
# exactly the entrusted folder:
#   godcode run --sandbox --allow-read examples/accountable_agent_data examples/accountable_agent.god
#
# Without the host grant the same run is refused. With the grant, a
# scroll that reaches past the folder is refused too. Run it twice
# and every line matches: the report is deterministic, so anyone can
# re-run it and compare, and it is ready to be sealed as a replayable
# receipt. See docs/accountable-agent.md.

BEGIN CREATION
  DECLARE PERMISSION TO READ "accountable_agent_data"

  DECLARE INTENT "to read only the entrusted folder and report every file in it honestly" ON survey
  DEFINE RITE survey(dir)
    DECLARE entries AS LIST_DIR(dir)
    DECLARE total_files AS 0
    DECLARE total_chars AS 0
    DECLARE ledger AS ""
    DECLARE i AS 0
    WHILE i < LEN(entries) DO
      DECLARE name AS entries[i]
      DECLARE text AS READ_FILE(dir + "/" + name)
      DECLARE chars AS LEN(text)
      DECLARE fingerprint AS SHA256(text)
      REVEAL("{name} holds {chars} characters, fingerprinted {fingerprint}.")
      DECLARE ledger AS ledger + name + "=" + fingerprint + ";"
      DECLARE total_files AS total_files + 1
      DECLARE total_chars AS total_chars + chars
      DECLARE i AS i + 1
    ENDWHILE
    REVEAL("Files counted: {total_files}")
    REVEAL("Total characters: {total_chars}")
    REVEAL("Report fingerprint: " + SHA256(ledger))
    RETURN total_files
  END RITE

  DECLARE data_dir AS "examples/accountable_agent_data"
  IF FILE_EXISTS(data_dir) THEN
    DECLARE counted AS survey(data_dir)
    REVEAL("Surveyed {counted} files. Nothing outside the entrusted folder was touched.")
  ELSE
    REVEAL("The entrusted folder is missing. Nothing to report.")
  ENDIF
END CREATION
