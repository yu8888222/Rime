-- 长按 Shift 临时英文处理器
-- 行为：
--   1. 有编码时按下 Shift：不拦截，交给 ascii_composer 执行 commit_code（短按流程不变）
--   2. 无编码时按下 Shift：记录进入临时英文模式，切换到英文
--      - 若按下后没有其他按键（短按），松开时切回中文（相当于短按无副作用）
--        但若你希望短按能切换中英文，此处保留 hold_shift 标记，松开时若未输入过其他键则切换一次
--   3. 无编码时按住 Shift 期间：保持英文输入
--   4. 松开 Shift：切回中文
-- 短按判定：按下与松开之间没有其他按键事件

local XK_Shift_L = 0xffe1
local XK_Shift_R = 0xffe2
local rime = require "sbxlm.lib"

local this = {}

---@class HoldShiftEnv: Env
---@field hold_shift boolean 是否处于长按临时英文状态
---@field had_other_key 按下 Shift 后是否按下过其他键（用于区分短按）

function this.init(env)
  env.hold_shift = false
  env.had_other_key = false
end

---@param key_event KeyEvent
---@param env HoldShiftEnv
function this.func(key_event, env)
  local context = env.engine.context
  local keycode = key_event.keycode

  -- 长按 Shift 临时英文模式期间，字母键转小写输入
  -- 由于物理上 Shift 仍按住，字母会带 Shift 修饰符被识别为大写
  -- 这里拦截 A-Z，用 engine:process_key 重新发一个不带 Shift 的小写字母事件
  if env.hold_shift and not key_event:release()
     and not key_event:alt() and not key_event:ctrl() and not key_event:super() then
    -- A-Z（带 Shift 修饰符）
    if keycode >= 0x41 and keycode <= 0x5a then
      env.had_other_key = true
      local ch = string.char(keycode + 32)
      -- 先释放 Shift（让 ascii_composer 忘掉 shift 状态），再注入小写字母
      env.engine:process_key(rime.KeyEvent("Release+" .. ch))
      env.engine:process_key(rime.KeyEvent(ch))
      return rime.process_results.kAccepted
    end
    -- a-z（某些前端在 ascii_mode 下可能不挂 Shift 修饰符）
    if keycode >= 0x61 and keycode <= 0x7a then
      env.had_other_key = true
      return rime.process_results.kNoop
    end
  end

  -- 只处理 Shift_L / Shift_R
  if keycode ~= XK_Shift_L and keycode ~= XK_Shift_R then
    -- 记录其他按键
    if env.hold_shift and not key_event:release() then
      env.had_other_key = true
    end
    return rime.process_results.kNoop
  end

  -- 松开事件
  if key_event:release() then
    if env.hold_shift then
      local was_short = not env.had_other_key
      env.hold_shift = false
      env.had_other_key = false
      if was_short then
        -- 短按：保持按下时已切换的状态（中→英 或 英→中），不额外操作
        env.was_english_on_press = nil
      else
        -- 长按：恢复到按下前的模式
        context:set_option("ascii_mode", env.was_english_on_press)
        env.was_english_on_press = nil
      end
      return rime.process_results.kAccepted
    end
    return rime.process_results.kNoop
  end

  -- 按下事件
  local ascii_mode = context:get_option("ascii_mode")

  -- 有编码：不拦截，让 ascii_composer 执行 commit_code（短按流程不变）
  if context:is_composing() then
    return rime.process_results.kNoop
  end

  -- 无编码时：进入长按临时英文/中文切换模式
  -- 记录按下时所处的模式，松开时若为短按则翻转一次（短按切换）
  env.hold_shift = true
  env.had_other_key = false
  env.was_english_on_press = ascii_mode
  -- 立即切换到目标模式：中文→英文，英文→中文
  context:set_option("ascii_mode", not ascii_mode)
  return rime.process_results.kAccepted
end

return this
