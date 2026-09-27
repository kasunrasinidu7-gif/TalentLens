"""Train and save the TalentLens matching model on the current live corpus."""

from backend.main import load_matcher


if __name__ == "__main__":
    model = load_matcher()
    print(model.metadata())
