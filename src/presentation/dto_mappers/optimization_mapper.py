"""Mappers for converting between DTOs and display models.

This module provides utilities for mapping application DTOs to
presentation-specific models if needed for complex UI requirements.
"""

from dataclasses import dataclass

from application.dto.optimization_dto import OptimizationDTO


@dataclass(frozen=True)
class OptimizationDisplayModel:
	"""Display model for optimization results in CLI.

	This model extends the DTO with presentation-specific formatting
	and computed properties for display purposes.

	Attributes:
		dto: Original optimization DTO
	"""

	dto: OptimizationDTO

	@property
	def formatted_database(self) -> str:
		"""Get formatted database type for display.

		Returns:
			Uppercase database type with emoji
		"""
		emoji_map = {
			"oracle": "🔶",
			"sqlite": "🔷",
			"sqlserver": "🔵",
			"postgresql": "🐘",
			"mysql": "🐬",
		}
		emoji = emoji_map.get(self.dto.database_type, "🗄️")
		return f"{emoji} {self.dto.database_type.upper()}"

	@property
	def query_preview(self) -> str:
		"""Get preview of optimized query.

		Returns:
			First 100 characters of optimized query
		"""
		return (
			self.dto.optimized_query[:100] + "..."
			if len(self.dto.optimized_query) > 100
			else self.dto.optimized_query
		)

	@property
	def explanation_preview(self) -> str:
		"""Get preview of explanation.

		Returns:
			First 150 characters of explanation
		"""
		return (
			self.dto.explanation[:150] + "..."
			if len(self.dto.explanation) > 150
			else self.dto.explanation
		)

	@property
	def query_stats(self) -> dict[str, int]:
		"""Get statistics about the queries.

		Returns:
			Dictionary with query statistics
		"""
		return {
			"original_length": len(self.dto.original_query),
			"optimized_length": len(self.dto.optimized_query),
			"explanation_length": len(self.dto.explanation),
			"size_change": len(self.dto.optimized_query) - len(self.dto.original_query),
		}

	@property
	def size_change_indicator(self) -> str:
		"""Get indicator showing query size change.

		Returns:
			String showing size change with arrow
		"""
		change = self.query_stats["size_change"]
		if change > 0:
			return f"↗️ +{change} chars"
		elif change < 0:
			return f"↘️ {change} chars"
		else:
			return "→ No change"


class OptimizationMapper:
	"""Mapper for converting DTOs to display models.

	This class provides static methods for converting between
	application DTOs and presentation display models.

	Examples:
		>>> display_model = OptimizationMapper.to_display_model(dto)
		>>> print(display_model.formatted_database)
	"""

	@staticmethod
	def to_display_model(dto: OptimizationDTO) -> OptimizationDisplayModel:
		"""Convert DTO to display model.

		Args:
			dto: Optimization DTO from application layer

		Returns:
			Display model for presentation layer
		"""
		return OptimizationDisplayModel(dto)

	@staticmethod
	def to_display_models(
		dtos: list[OptimizationDTO],
	) -> list[OptimizationDisplayModel]:
		"""Convert multiple DTOs to display models.

		Args:
			dtos: List of optimization DTOs

		Returns:
			List of display models
		"""
		return [OptimizationMapper.to_display_model(dto) for dto in dtos]
