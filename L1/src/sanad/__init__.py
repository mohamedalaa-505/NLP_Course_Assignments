"""Sanad, the university help-desk assistant built level by level in the Lab Manual.

Three services share one text-preparation pipeline:
  router   ticket -> intent (+ slots, reply)
  search   question -> ranked FAQ passages
  keyboard typed words -> next-word suggestions
Each service and each shared part has numbered versions (v0, v1, ...). A new
version never replaces the file of an old one; sanad.toml chooses which runs.
"""
LEVEL = 0
