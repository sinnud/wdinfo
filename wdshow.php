<!--
included by index.php
In this module, you can:

1. dynamically select folder and subfolder to get fullpath of one file
2. 
3. 
-->
<h1>WD net drive 192.168.1.243: dir and file</h1>
<form>
<select name="root" onchange="showRoot(this.value)">
  <option value="">Select a root:</option>
  <option value="1">photos</option>
  <option value="2">data</option>
  <option value="3">music</option>
  <option value="4">movie</option>
  </select>
</form>
<br>

<p>Sample data: <span id="txtHint"></span></p>