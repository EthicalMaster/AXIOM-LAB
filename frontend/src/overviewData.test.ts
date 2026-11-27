import {describe,it,expect} from 'vitest';
import {previewPoints,profileSummary} from './overviewData';
import type {DatasetColumnProfile} from './columnProfile';
describe('Overview evidence',()=>{
 it('skips missing and nonfinite values without compressing row order',()=>{
  expect(previewPoints({headers:['x'],preview:[['0'],[null],[' '],['-2.5'],['Infinity'],['abc']]},'x')).toEqual([{x:1,y:0},{x:4,y:-2.5}]);
 });
 it('does not invent values for unknown columns',()=>{
  expect(previewPoints({headers:['x'],preview:[['1']]},'y')).toEqual([]);
 });
 it('uses the full profile instead of the bounded preview',()=>{
  const p:DatasetColumnProfile={dataset_id:'test',row_count:80,column_count:2,worksheet:null,method_note:'',columns:[{name:'x',inferred_type:'numeric',non_missing_count:80,missing_count:0,distinct_count:80,distinct_count_exact:true,examples:[],warnings:[]},{name:'y',inferred_type:'numeric',non_missing_count:60,missing_count:20,distinct_count:60,distinct_count_exact:true,examples:[],warnings:[]}]};
  expect(profileSummary(p)).toEqual({missing:20,completeness:87.5,types:[['numeric',2]]});
 });
 it('distinguishes missing profiles from perfect completeness',()=>{
  expect(profileSummary(null).completeness).toBeNull();
 });
});
