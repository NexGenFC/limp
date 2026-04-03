from django.db import models


class District(models.Model):
    name = models.CharField(max_length=128, unique=True)
    state = models.CharField(max_length=64, default="Karnataka")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "districts"

    def __str__(self) -> str:
        return self.name


class Taluk(models.Model):
    name = models.CharField(max_length=128)
    district = models.ForeignKey(
        District, related_name="taluks", on_delete=models.PROTECT
    )

    class Meta:
        ordering = ["name"]
        unique_together = [("name", "district")]
        verbose_name_plural = "taluks"

    def __str__(self) -> str:
        return f"{self.name}, {self.district.name}"


class Hobli(models.Model):
    name = models.CharField(max_length=128)
    taluk = models.ForeignKey(Taluk, related_name="hoblis", on_delete=models.PROTECT)

    class Meta:
        ordering = ["name"]
        unique_together = [("name", "taluk")]
        verbose_name_plural = "hoblis"

    def __str__(self) -> str:
        return f"{self.name}, {self.taluk.name}"


class Village(models.Model):
    name = models.CharField(max_length=128)
    hobli = models.ForeignKey(Hobli, related_name="villages", on_delete=models.PROTECT)

    class Meta:
        ordering = ["name"]
        unique_together = [("name", "hobli")]
        verbose_name_plural = "villages"

    def __str__(self) -> str:
        return f"{self.name}, {self.hobli.name}"
