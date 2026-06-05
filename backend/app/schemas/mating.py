from datetime import date

from pydantic import BaseModel, model_validator


class MatingBase(BaseModel):
    sire_id: int
    dam_id: int
    mating_date: date | None = None
    litter_dob: date | None = None
    litter_size: int | None = None
    male_pups: int | None = None
    female_pups: int | None = None
    pup_genotypes: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_mice_and_litter(self):
        if self.sire_id == self.dam_id:
            raise ValueError("Sire and dam must be different mice")

        if (
            self.litter_size is not None
            and self.male_pups is not None
            and self.female_pups is not None
            and self.male_pups + self.female_pups > self.litter_size
        ):
            raise ValueError("Male and female pup counts cannot exceed litter size")

        return self


class MatingCreate(MatingBase):
    pass


class MatingRead(MatingBase):
    id: int

    class Config:
        from_attributes = True
