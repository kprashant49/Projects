Select *, count(brick_id) over(partition by colour) as total_bricks from bricks;
Select *, sum(weight) over(partition by colour) as total_weight from bricks;
Select *, sum(weight) over(partition by shape) as total_weight from bricks;

Select *,
sum(weight) over(partition by shape) as total_weight_shape,
sum(weight) over(partition by colour) as total_weight_colour,
max(weight) over(partition by shape) as max_weight_shape,
max(weight) over(partition by colour) as max_weight_colour
from bricks;

Select *,
count(*) over(order by brick_id) as running_count
from bricks;

Select *,
sum(weight) over(order by brick_id) as running_weight
from bricks;

Select *,
sum(weight) over(partition by colour order by brick_id) as running_weight_by_colour
from bricks
order by brick_id;