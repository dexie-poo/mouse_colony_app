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
    genotyping_reference: str | None = None
    keep_litter: bool | None = False
    euthanise_litter: bool | None = False
    kept_male_pups: int | None = None
    kept_female_pups: int | None = None
    kept_pup_genotype: str | None = None
    notes: str | None = None
    pups: list["LitterPupCreate"] = []

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
    kept_mouse_ids: str | None = None

    class Config:
        from_attributes = True


class LitterPupCreate(BaseModel):
    pup_label: str | None = None
    assigned_external_id: str | None = None
    sex: str
    wean_date: date | None = None
    genotype: str | None = None
    genotype_reference_1: str | None = None
    genotype_reference_2: str | None = None
    decision: str


class LitterPupRead(LitterPupCreate):
    id: int
    mating_id: int
    mouse_id: int | None = None
    dob: date | None = None

    class Config:
        from_attributes = True
