# Mixed Precision Quantization

## Quantization

### Why does it work?
Integers have very straightforward representation. signed integers store their numbers in base 2 with no additional overhead(except for the sign, but that's irrelevant), making calculations per cycle in a model really really efficient.Compare that to FP16(floating point number) with the following idea : 
![Preview of gui]({{ '/images/f16rep.png?v=1' | relative_url }})

### What is quantization?
LLM weights are stored in high-precision formats (such as 16-bit FP16 or 32-bit FP32), but with quantization, this is reduced by mapping weights to lower-precision formats (such as 8-bit INT8 or 4-bit INT4) to save memory and speed up inference.

![Preview of gui]({{ '/images/quavis.png?v=1' | relative_url }})

this is the IEEE standard, many other standards are in the world. but just look at how complex this is.
As you'd expect floating point operations take A LOT more compute. No hassle for a good gpu, but for local GPUs / Integrated graphics. Floating operations take 3-4 clock cycles depending on the representation and the number itself, just know that it's 3-4x more than integers.

### If it's so good, why don't all AIs use it to the max?
AIs do use quantization, but quantization, as shown in the first image, damages accuracy. Whilst most models come with redundant weights, meaning that a little quantization is usually ok (AIs that are meant to run locally do that... like A LOT). But it's always a tricky balance to strike between quantization and efficiency/intelligence, to maintain PRECISION.

## Mixed Precision
### Why Mixed Precision?
Not all layers in a neural network are equally sensitive to precision loss. Mixed precision quantization applies lower bit-widths (e.g., 4-bit) to less critical layers and higher bit-widths (e.g., 8-bit or 16-bit) to sensitive layers, achieving the optimal balance between model size, memory usage, and accuracy. Instead of just setting every value to an approximate number. 



[Information from video](https://www.youtube.com/watch?v=qoQJq5UwV1c)
[image 1 source](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization)
[image 2 source](https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fwww.linkedin.com%2Fpulse%2Ffloat32-vs-float16-bfloat16-damien-benveniste-av3oc&ved=0CBsQ3YkBahcKEwjw3p-UrIyYAxUAAAAAHQAAAAAQaQ&opi=89978449)


