// src/ai/flows/categorize-and-respond.ts
'use server';

/**
 * @fileOverview This file defines a Genkit flow for categorizing user inquiries and providing relevant responses.
 *
 * - categorizeAndRespond - A function that takes a user's input (text or voice) and returns a categorized response.
 * - CategorizeAndRespondInput - The input type for the categorizeAndRespond function.
 * - CategorizeAndRespondOutput - The return type for the categorizeAndRespond function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const CategorizeAndRespondInputSchema = z.object({
  userInput: z.string().describe('The user input, either text or voice input.'),
});

export type CategorizeAndRespondInput = z.infer<typeof CategorizeAndRespondInputSchema>;

const CategorizeAndRespondOutputSchema = z.object({
  category: z.string().describe('The category of the user inquiry (e.g., crop advice, market prices).'),
  response: z.string().describe('The relevant and accurate response to the user inquiry.'),
});

export type CategorizeAndRespondOutput = z.infer<typeof CategorizeAndRespondOutputSchema>;


export async function categorizeAndRespond(input: CategorizeAndRespondInput): Promise<CategorizeAndRespondOutput> {
  return categorizeAndRespondFlow(input);
}

const cropAdviceTool = ai.defineTool({
  name: 'getCropAdvice',
  description: 'Provides advice on crop cultivation, pest control, and disease management.',
  inputSchema: z.object({
    query: z.string().describe('Specific question about crop cultivation, pests, or diseases.'),
  }),
  outputSchema: z.string(),
}, async (input) => {
  // Placeholder implementation for fetching crop advice
  return `Crop advice for: ${input.query}. Please consult with a local expert for specific guidance.`
});

const marketPricesTool = ai.defineTool({
  name: 'getMarketPrices',
  description: 'Retrieves current market prices for various crops.',
  inputSchema: z.object({
    cropName: z.string().describe('The name of the crop to get the market price for.'),
  }),
  outputSchema: z.string(),
}, async (input) => {
  // Placeholder implementation for fetching market prices
  return `Market price for ${input.cropName} is currently $X per unit.`
});

const prompt = ai.definePrompt({
  name: 'categorizeAndRespondPrompt',
  input: {schema: CategorizeAndRespondInputSchema},
  output: {schema: CategorizeAndRespondOutputSchema},
  tools: [cropAdviceTool, marketPricesTool],
  prompt: `You are an expert farming assistant. Your task is to analyze the user's question, categorize it, and then use the appropriate tool to generate a response. If the user's query does not fit into "crop advice" or "market prices", you must still choose the most relevant category and provide a helpful response.

You MUST perform the following steps:
1.  Read the user's input.
2.  Determine if the question is about "crop advice" or "market prices".
3.  Based on the category, you MUST call the corresponding tool ('getCropAdvice' or 'getMarketPrices'). You absolutely must call one of these tools.
4.  Use the output from the tool to construct the final response.
5.  Set the 'category' and 'response' fields in your JSON output. Your response MUST be a valid JSON object matching the required schema.

User Input: {{{userInput}}}
`,
});

const categorizeAndRespondFlow = ai.defineFlow(
  {
    name: 'categorizeAndRespondFlow',
    inputSchema: CategorizeAndRespondInputSchema,
    outputSchema: CategorizeAndRespondOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    if (!output) {
      // Handle cases where the model might not return a valid structured response
      return {
        category: 'general',
        response: "I'm sorry, I couldn't process that request. Could you please rephrase it?"
      };
    }
    return output;
  }
);
