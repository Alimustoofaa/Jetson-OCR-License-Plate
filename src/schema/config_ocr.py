from pydantic import BaseModel
from typing import Optional

class ConfigOcr(BaseModel):
	# General config
	decoder:        Optional[str]   = 'greedy'
	beam_width:     Optional[int]   = 5
	batch_size:     Optional[int]   = 1
	workers:        Optional[int]   = 4
	allow_list:     Optional[str]   = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	blocklist:      Optional[str]   = ''
	detail:         Optional[int]   = 1
	paragraph:      Optional[bool]  = False
	min_size:       Optional[int]   = 10
	rotation_info:  Optional[list]  = None

	# Contrast
	contrast_ths:    Optional[float] = 0.1
	adjust_contrast: Optional[float] = 0.5

	# Text detection
	text_threshold: Optional[float] = 0.7
	low_text:       Optional[float] = 0.4
	link_threshold: Optional[float] = 0.4
	canvas_size:    Optional[int]   = 2560
	mag_ratio:      Optional[int]   = 1